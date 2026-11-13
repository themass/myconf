#!/usr/bin/env bash
# 多机管理入口：在脚本机上一条命令管理全部服务器（状态、同步代码、部署、VPN 节点增减和重启、radius 增加 IP）。
# 本机只做调度，实际安装仍由各机器上的 infra.sh / vpn.sh / radius.sh 完成。
#
#   bash fleet.sh hosts                          列出清单
#   bash fleet.sh status [目标]                  各机服务状态（只读）
#   bash fleet.sh run <目标> <命令...>           在目标机器上执行命令
#   bash fleet.sh sync [目标]                    目标机器上 git pull --ff-only
#   bash fleet.sh deploy <软件> [目标]           sync 后执行 infra.sh <软件>（nginx|redis|mysql|radius|jdk|php|postgres）
#   bash fleet.sh vpn add <ip> [端口] [--deploy] 登记 VPN 节点 + 加进 radius clients（--deploy 另在节点上部署）
#   bash fleet.sh vpn del <ip>                   从清单和 radius clients 去掉（不动节点上已运行的服务）
#   bash fleet.sh vpn restart [目标]             逐台重启 VPN 服务并检查状态（默认全部 vpn 节点）
#   bash fleet.sh radius add-ip <ip>             只加 radius 客户端 IP 并推送
#   bash fleet.sh radius del-ip <ip>
#   bash fleet.sh radius list | push
#
# 目标: all | 角色名(vpn nginx infra login app ...) | IP。清单和账号在仓库根目录的 .env（已被 git 忽略，
# 复制到脚本机即可使用），格式见 .env.example。

if [ -z "${BASH_VERSION:-}" ]; then
    command -v bash >/dev/null 2>&1 && exec bash "$0" "$@"
    echo "需要 bash: bash $0 ..." >&2
    exit 2
fi

VPN_SHELL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export VPN_SHELL_DIR
# shellcheck source=lib/common.sh
source "${VPN_SHELL_DIR}/lib/common.sh"

FLEET_ENV="${FLEET_ENV:-${MYCONF_HOME}/.env}"
CLIENTS_CONF="${MYCONF_HOME}/conf/radius/clients.conf"

# ------------------------------------------------------------------ 配置与清单

fleet_load_env() {
    [ -f "$FLEET_ENV" ] || die "缺少 ${FLEET_ENV}。参照 .env.example 的 FLEET_ 部分创建（该文件不进 git）"
    set -a
    # shellcheck disable=SC1090
    source "$FLEET_ENV"
    set +a
    FLEET_USER="${FLEET_USER:-root}"
    FLEET_REMOTE_DIR="${FLEET_REMOTE_DIR:-/root/work/myconf}"
    FLEET_BRANCH="${FLEET_BRANCH:-}"
    [ -n "${FLEET_HOSTS:-}" ] || die "${FLEET_ENV} 里没有 FLEET_HOSTS"
}

# 输出 "ip port roles" 每台一行。清单每行: ip:端口:角色,角色   端口留空按 22。
fleet_all_hosts() {
    printf '%s\n' "$FLEET_HOSTS" | awk -F: 'NF >= 1 && $1 !~ /^[[:space:]]*(#|$)/ {
        gsub(/[[:space:]]/, "", $1); gsub(/[[:space:]]/, "", $2); gsub(/[[:space:]]/, "", $3)
        print $1, ($2 == "" ? 22 : $2), ($3 == "" ? "-" : $3) }'
}

# fleet_select <目标...>  展开成 "ip port roles" 行。没匹配到任何机器就报错。
fleet_select() {
    local t out="" line
    for t in "$@"; do
        line="$(fleet_all_hosts | awk -v t="$t" '
            t == "all" || $1 == t { print; next }
            { n = split($3, r, ","); for (i = 1; i <= n; i++) if (r[i] == t) { print; break } }')"
        [ -n "$line" ] || die "清单里没有匹配的机器: ${t}（bash fleet.sh hosts 查看）"
        out="${out}${line}"$'\n'
    done
    printf '%s' "$out" | awk 'NF && !seen[$1]++'
}

# ------------------------------------------------------------------ SSH（密码用 expect，有密钥就直接 ssh）

FLEET_EXP=""
fleet_expect_script() {
    [ -n "$FLEET_EXP" ] && return 0
    have expect || die "用密码登录需要 expect；或者给目标机器装好密钥并清空 FLEET_PASSWORD"
    FLEET_EXP="$(mktemp "${TMPDIR:-/tmp}/fleet-exp.XXXXXX")"
    cat >"$FLEET_EXP" <<'EXP'
set timeout $env(F_TIMEOUT)
log_user 1
spawn {*}$argv
expect {
    -re "yes/no" { send "yes\r"; exp_continue }
    -re "assword:" { send "$env(F_PW)\r"; exp_continue }
    timeout { puts "\n[fleet] 超时"; exit 124 }
    eof
}
catch wait r
exit [lindex $r 3]
EXP
    trap 'rm -f "$FLEET_EXP"' EXIT
}

# 密码: FLEET_PASSWORD_<ip 把点换成下划线> 优先于 FLEET_PASSWORD
fleet_pw() {
    local var="FLEET_PASSWORD_${1//./_}"
    printf '%s' "${!var:-${FLEET_PASSWORD:-}}"
}

FLEET_SSH_OPTS=(-o StrictHostKeyChecking=accept-new -o ConnectTimeout=10 -o ServerAliveInterval=15 -o LogLevel=ERROR)

# fleet_cmd <ip> <argv...>  用密码就走 expect，否则直接执行（BatchMode）。
fleet_cmd() {
    local ip="$1" pw rc
    shift
    pw="$(fleet_pw "$ip")"
    if [ -n "$pw" ]; then
        fleet_expect_script
        # 去掉 expect 打印的 spawn 行和密码提示，只留远端输出。
        F_PW="$pw" F_TIMEOUT="${FLEET_TIMEOUT:-900}" expect -f "$FLEET_EXP" -- "$@" \
            | tr -d '\r' | sed -e '/^spawn /d' -e 's/^.*[Pp]assword: *//'
        return "${PIPESTATUS[0]}"
    fi
    "$@"
    rc=$?
    return $rc
}

# fleet_ssh <ip> <port> <远程命令...>
fleet_ssh() {
    local ip="$1" port="$2"
    shift 2
    local opts=("${FLEET_SSH_OPTS[@]}")
    [ -z "$(fleet_pw "$ip")" ] && opts+=(-o BatchMode=yes)
    fleet_cmd "$ip" ssh -p "$port" "${opts[@]}" "${FLEET_USER}@${ip}" "$*"
}

# fleet_put <ip> <port> <本地文件> <远程路径>
fleet_put() {
    local ip="$1" port="$2"
    local opts=("${FLEET_SSH_OPTS[@]}")
    [ -z "$(fleet_pw "$ip")" ] && opts+=(-o BatchMode=yes)
    fleet_cmd "$ip" scp -P "$port" "${opts[@]}" "$3" "${FLEET_USER}@${ip}:$4"
}

# fleet_each <目标> <函数> [参数...]  对每台机器调用 函数 ip port roles 参数...；某台失败继续，最后汇总。
fleet_each() {
    local target="$1" fn="$2" ip port roles failed="" total=0
    shift 2
    while read -r ip port roles; do
        [ -n "$ip" ] || continue
        total=$((total + 1))
        echo "== ${ip} (${roles}) =="
        "$fn" "$ip" "$port" "$roles" "$@" || failed="${failed} ${ip}"
    done < <(fleet_select "$target")
    if [ -n "$failed" ]; then
        err "失败的机器:${failed}"
        return 1
    fi
    log "完成，共 ${total} 台"
}

# ------------------------------------------------------------------ 基础动作

do_status() {
    fleet_ssh "$1" "$2" "hostname; uptime -p 2>/dev/null; \
for u in nginx openresty redis-server redis mysql mysqld postgresql freeradius strongswan xray sing-box wg-quick@wg0; do \
s=\$(systemctl is-active \$u 2>/dev/null); case \$s in active|failed) echo \"  \$u \$s\";; esac; done; \
echo \"  repo: \$(cd ${FLEET_REMOTE_DIR} 2>/dev/null && git rev-parse --short HEAD 2>/dev/null || echo 无)\""
}

do_run() { fleet_ssh "$1" "$2" "${@:4}"; }

do_sync() {
    local branch_cmd=""
    [ -n "$FLEET_BRANCH" ] && branch_cmd="git checkout ${FLEET_BRANCH} && "
    fleet_ssh "$1" "$2" "cd ${FLEET_REMOTE_DIR} && ${branch_cmd}git pull --ff-only && git log --oneline -1"
}

do_deploy() { # ip port roles 软件
    do_sync "$1" "$2" || return 1
    fleet_ssh "$1" "$2" "cd ${FLEET_REMOTE_DIR}/shell && bash infra.sh $4"
}

deploy_default_target() {
    case "$1" in
        nginx) echo nginx ;;
        *) echo infra ;;
    esac
}

# ------------------------------------------------------------------ radius clients

valid_ipv4() {
    local ip="$1" o
    [[ "$ip" =~ ^([0-9]{1,3}\.){3}[0-9]{1,3}$ ]] || return 1
    local IFS=.
    for o in $ip; do [ "$o" -le 255 ] || return 1; done
}

radius_has_ip() { grep -qE "^[[:space:]]*ipaddr[[:space:]]*=[[:space:]]*${1//./\\.}[[:space:]]*$" "$CLIENTS_CONF"; }

radius_add_client() {
    local ip="$1" secret
    valid_ipv4 "$ip" || die "不是合法的 IPv4: ${ip}"
    if radius_has_ip "$ip"; then
        log "clients.conf 里已有 ${ip}"
        return 0
    fi
    secret="${FLEET_RADIUS_SECRET:-$(awk '$1 == "secret" { s = $3 } END { print s }' "$CLIENTS_CONF")}"
    [ -n "$secret" ] || die "取不到 radius 共享密钥，请在 .env 设置 FLEET_RADIUS_SECRET"
    # shortname 必须保持 vpn_check，线上策略按这个名字匹配。
    cat >>"$CLIENTS_CONF" <<EOF

client ${ip} {
    ipaddr        = ${ip}
    secret        = ${secret}
    shortname     = vpn_check
    require_message_authenticator = no
    limit_proxy_state = yes
}
EOF
    log "clients.conf 已加入 ${ip}"
}

radius_del_client() {
    local ip="$1" tmp
    valid_ipv4 "$ip" || die "不是合法的 IPv4: ${ip}"
    radius_has_ip "$ip" || { log "clients.conf 里没有 ${ip}"; return 0; }
    tmp="$(mktemp "${TMPDIR:-/tmp}/clients.XXXXXX")"
    awk -v ip="$ip" '
        BEGIN { re = ip; gsub(/\./, "\\.", re) }
        skip { if ($0 ~ /^}/) skip = 0; next }
        # 块前面的那一个空行（add 时加的）跟着一起去掉，来回增删不留痕迹。
        /^[[:space:]]*$/ { if (held) print ""; held = 1; next }
        $0 ~ "^client[[:space:]]+" re "[[:space:]]*\\{" { skip = 1; held = 0; next }
        { if (held) print ""; held = 0; print }
        END { if (held) print "" }' "$CLIENTS_CONF" >"$tmp"
    if radius_has_ip_in "$tmp" "$ip"; then
        rm -f "$tmp"
        die "删除 ${ip} 失败，clients.conf 没有改动"
    fi
    cat "$tmp" >"$CLIENTS_CONF"
    rm -f "$tmp"
    log "clients.conf 已去掉 ${ip}"
}

radius_has_ip_in() { grep -qE "^[[:space:]]*ipaddr[[:space:]]*=[[:space:]]*${2//./\\.}[[:space:]]*$" "$1"; }

# 把本地 clients.conf 推到 radius 机并让 radius.sh 校验、重启（校验失败它会自动还原）。
radius_push() {
    local ip port roles n=0
    [ -f "$CLIENTS_CONF" ] || die "缺少 ${CLIENTS_CONF}"
    while read -r ip port roles; do
        [ -n "$ip" ] || continue
        n=$((n + 1))
        echo "== ${ip} (radius) =="
        fleet_put "$ip" "$port" "$CLIENTS_CONF" /tmp/clients.conf.fleet || return 1
        # radius.sh 只认仓库里的 clients.conf：临时覆盖 -> 校验并重启 -> 还原仓库文件（线上 /etc 里的保持新内容），
        # 这样远端仓库不会因为本地改动导致下次 git pull 冲突。
        fleet_ssh "$ip" "$port" "cd ${FLEET_REMOTE_DIR} && cp /tmp/clients.conf.fleet conf/radius/clients.conf \
&& rm -f /tmp/clients.conf.fleet && (cd shell && bash radius.sh clients); rc=\$?; \
git checkout -- conf/radius/clients.conf; exit \$rc" || return 1
    done < <(fleet_select radius)
    [ "$n" -gt 0 ] || die "清单里没有 radius 角色的机器"
    warn "记得在本机 git commit + push conf/radius/clients.conf，仓库和线上才一致"
}

radius_main() {
    local action="${1:-}"
    [ $# -gt 0 ] && shift
    case "$action" in
        add-ip)
            [ -n "${1:-}" ] || die "用法: fleet.sh radius add-ip <ip>"
            radius_add_client "$1" && radius_push
            ;;
        del-ip)
            [ -n "${1:-}" ] || die "用法: fleet.sh radius del-ip <ip>"
            radius_del_client "$1" && radius_push
            ;;
        list) grep -E '^[[:space:]]*ipaddr' "$CLIENTS_CONF" | awk '{print $3}' ;;
        push) radius_push ;;
        *) die "用法: fleet.sh radius add-ip|del-ip <ip> | list | push" ;;
    esac
}

# ------------------------------------------------------------------ VPN 节点

# 在 .env 的 FLEET_HOSTS 里增删一行（清单是以单独一行 " 结尾的多行字符串）。
inventory_add() { # ip port roles
    local ip="$1" port="$2" roles="$3" tmp
    if fleet_all_hosts | awk -v ip="$ip" '$1 == ip { f = 1 } END { exit !f }'; then
        log "清单里已有 ${ip}"
        return 0
    fi
    tmp="$(mktemp "${TMPDIR:-/tmp}/env.XXXXXX")"
    awk -v line="${ip}:${port}:${roles}" '
        /^FLEET_HOSTS="/ { inblk = 1 }
        inblk && /^"[[:space:]]*$/ { print line; inblk = 0 }
        { print }' "$FLEET_ENV" >"$tmp"
    cmp -s "$tmp" "$FLEET_ENV" && { rm -f "$tmp"; die "没能写入清单：.env 里 FLEET_HOSTS 需要是以单独一行 \" 结尾的多行写法"; }
    cat "$tmp" >"$FLEET_ENV"
    rm -f "$tmp"
    log "清单已加入 ${ip}:${port}:${roles}"
}

inventory_del() {
    local ip="$1" tmp
    tmp="$(mktemp "${TMPDIR:-/tmp}/env.XXXXXX")"
    awk -v ip="$ip" '
        /^FLEET_HOSTS="/ { inblk = 1; print; next }
        inblk && /^"[[:space:]]*$/ { inblk = 0 }
        inblk { split($0, f, ":"); gsub(/[[:space:]]/, "", f[1]); if (f[1] == ip) next }
        { print }' "$FLEET_ENV" >"$tmp"
    cat "$tmp" >"$FLEET_ENV"
    rm -f "$tmp"
    log "清单已去掉 ${ip}"
}

# 只重启在跑的 VPN 服务。strongswan 走 vpn.sh（重启后重新加载 swanctl.conf）。
do_vpn_restart() {
    fleet_ssh "$1" "$2" "cd ${FLEET_REMOTE_DIR}/shell || exit 1; rc=0; n=0; \
if systemctl cat strongswan >/dev/null 2>&1; then n=\$((n+1)); bash vpn.sh strongswan restart || rc=1; fi; \
for u in xray sing-box wg-quick@wg0; do \
if systemctl is-enabled \$u >/dev/null 2>&1; then n=\$((n+1)); systemctl restart \$u || rc=1; fi; done; \
sleep 2; for u in strongswan xray sing-box wg-quick@wg0; do \
systemctl cat \$u >/dev/null 2>&1 || continue; s=\$(systemctl is-active \$u); echo \"  \$u \$s\"; [ \"\$s\" = active ] || rc=1; done; \
[ \$n -gt 0 ] || { echo '  没有找到 VPN 服务'; rc=1; }; exit \$rc"
}

do_vpn_deploy() {
    do_sync "$1" "$2" || return 1
    fleet_ssh "$1" "$2" "cd ${FLEET_REMOTE_DIR}/shell && ${FLEET_VPN_DEPLOY:-bash vpn.sh system init && bash vpn.sh strongswan all}"
}

vpn_main() {
    local action="${1:-}" ip port deploy=0 a rest=()
    [ $# -gt 0 ] && shift
    for a in "$@"; do
        case "$a" in
            --deploy) deploy=1 ;;
            *) rest+=("$a") ;;
        esac
    done
    set -- "${rest[@]+"${rest[@]}"}"
    case "$action" in
        add)
            ip="${1:-}" port="${2:-22}"
            valid_ipv4 "$ip" || die "用法: fleet.sh vpn add <ip> [ssh端口] [--deploy]"
            inventory_add "$ip" "$port" vpn
            radius_add_client "$ip"
            radius_push || die "radius 推送失败，节点还不能认证；修好后运行: fleet.sh radius push"
            if [ "$deploy" -eq 1 ]; then
                log "在 ${ip} 上部署 VPN（${FLEET_VPN_DEPLOY:-bash vpn.sh system init && bash vpn.sh strongswan all}）"
                do_vpn_deploy "$ip" "$port"
            else
                log "节点已登记。需要部署再加 --deploy，或运行: fleet.sh run ${ip} 'cd ${FLEET_REMOTE_DIR}/shell && bash vpn.sh ...'"
            fi
            ;;
        del)
            ip="${1:-}"
            valid_ipv4 "$ip" || die "用法: fleet.sh vpn del <ip>"
            inventory_del "$ip"
            radius_del_client "$ip"
            radius_push
            warn "${ip} 上已运行的服务没有动；要停掉请自己登录处理"
            ;;
        restart) fleet_each "${1:-vpn}" do_vpn_restart ;;
        list) fleet_select vpn ;;
        *) die "用法: fleet.sh vpn add <ip> [端口] [--deploy] | del <ip> | restart [目标] | list" ;;
    esac
}

# ------------------------------------------------------------------ 入口

fleet_usage() { sed -n '2,22p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'; }

fleet_main() {
    local cmd="${1:-}"
    [ $# -gt 0 ] && shift
    case "$cmd" in
        '' | help | -h | --help) fleet_usage; return 0 ;;
    esac
    fleet_load_env
    case "$cmd" in
        hosts) fleet_all_hosts | awk '{ printf "%-18s ssh:%-6s %s\n", $1, $2, $3 }' ;;
        status) fleet_each "${1:-all}" do_status ;;
        run)
            [ $# -ge 2 ] || die "用法: fleet.sh run <目标> <命令...>"
            local target="$1"
            shift
            fleet_each "$target" do_run "$@"
            ;;
        sync) fleet_each "${1:-all}" do_sync ;;
        deploy)
            [ -n "${1:-}" ] || die "用法: fleet.sh deploy <软件> [目标]"
            fleet_each "${2:-$(deploy_default_target "$1")}" do_deploy "$1"
            ;;
        vpn) vpn_main "$@" ;;
        radius) radius_main "$@" ;;
        *)
            err "未知命令: ${cmd}"
            fleet_usage
            return 2
            ;;
    esac
}

fleet_main "$@"
