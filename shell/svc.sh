#!/usr/bin/env bash
# 非 VPN 服务的启停、状态、检查、日志：nginx(OpenResty)、MySQL、FreeRADIUS、Redis。
# 取代旧的 start.sh / root_init.sh / radiusd.sh。安装见 infra.sh；VPN 服务见 vpn.sh health。
#
#   bash svc.sh status [服务...]            状态总览（默认）
#   bash svc.sh start|stop|restart [服务...]
#   bash svc.sh check                       深一层的检查：配置语法、端口、进程存活
#   bash svc.sh logs <服务> [-n 行数] [-f]
#
# 服务名: nginx mysql radius redis（别名: openresty / radiusd / redis-server），不写就是全部。
# 都走 systemd，不再 pkill -9。RADIUS 的 clients.conf 更新和调试见 radius.sh。后端 Spring Boot 的启停用它自己的 bin/start.sh、bin/stop.sh。

if [ -z "${BASH_VERSION:-}" ]; then
    command -v bash >/dev/null 2>&1 && exec bash "$0" "$@"
    echo "需要 bash: bash $0 ..." >&2
    exit 2
fi

VPN_SHELL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export VPN_SHELL_DIR
# shellcheck source=lib/common.sh
source "${VPN_SHELL_DIR}/lib/common.sh"

SVC_ALL="nginx mysql radius redis php postgres"
SVC_BAD=0

svc_usage() {
    cat <<EOF
用法: bash svc.sh <动作> [服务...]

  status  [服务...]          状态总览（默认动作）：是否运行、开机自启、已运行多久、监听端口
  start   [服务...]
  stop    [服务...]
  restart [服务...]
  check                      配置语法、端口监听、进程存活；有异常退出码为 1
  logs <服务> [-n N] [-f]    看日志（journal），-f 持续跟踪

服务: ${SVC_ALL}（不写就是全部）。顺序: 启动按 mysql radius redis nginx，停止反过来。
EOF
}

# 服务名 -> systemd 单元
svc_unit() {
    case "$1" in
        nginx | openresty) printf 'openresty' ;;
        mysql) printf 'mysql' ;;
        radius | radiusd) printf 'freeradius' ;;
        redis | redis-server) printf 'redis-server' ;;
        php | php-fpm) printf 'php%s-fpm' "${PHP_VERSION:-8.4}" ;;
        postgres | pg) printf 'postgresql@%s-main' "${PG_VERSION:-17}" ;;
        *) return 1 ;;
    esac
}

# 服务名 -> "协议/端口"；端口尽量从配置里读，读不到用默认值。
svc_port() {
    local p
    case "$1" in
        nginx) printf 'tcp/80' ;;
        mysql)
            # 8.0 起配置在 /etc/mysql/conf.d/；旧版 tarball 的在 /etc/my.cnf。
            p="$(sed -n 's/^port[[:space:]]*=[[:space:]]*\([0-9]*\).*/\1/p' /etc/mysql/mysql.conf.d/zz-vpn.cnf 2>/dev/null | head -n 1)"
            [ -n "$p" ] || p="$(sed -n 's/^port[[:space:]]*=[[:space:]]*\([0-9]*\).*/\1/p' /etc/my.cnf 2>/dev/null | head -n 1)"
            printf 'tcp/%s' "${p:-6666}"
            ;;
        redis)
            p="$(sed -n 's/^port[[:space:]]\{1,\}\([0-9]*\).*/\1/p' /etc/redis/redis.conf 2>/dev/null | head -n 1)"
            printf 'tcp/%s' "${p:-6379}"
            ;;
        postgres)
            p="$(sed -n 's/^port[[:space:]]*=[[:space:]]*\([0-9]*\).*/\1/p' "/etc/postgresql/${PG_VERSION:-17}/main/conf.d/90-vpn.conf" 2>/dev/null | head -n 1)"
            printf 'tcp/%s' "${p:-5432}"
            ;;
        radius) printf 'udp/1812' ;;
    esac
}

# 解析要操作的服务列表；没写就是全部。输出规范名，空格分隔。
svc_list() {
    local s out=""
    if [ $# -eq 0 ]; then
        printf '%s' "$SVC_ALL"
        return 0
    fi
    for s in "$@"; do
        case "$s" in
            nginx | openresty) out="${out} nginx" ;;
            mysql) out="${out} mysql" ;;
            radius | radiusd) out="${out} radius" ;;
            redis | redis-server) out="${out} redis" ;;
            php | php-fpm) out="${out} php" ;;
            postgres | pg | postgresql) out="${out} postgres" ;;
            *) die "未知服务: ${s}（可选: ${SVC_ALL}）" ;;
        esac
    done
    printf '%s' "$out"
}

svc_installed() { systemctl cat "$(svc_unit "$1")" >/dev/null 2>&1; }

svc_uptime() { # <unit>
    local ts then
    ts="$(systemctl show -p ActiveEnterTimestamp "$1" 2>/dev/null | cut -d= -f2-)"
    [ -n "$ts" ] || { printf -- '-'; return 0; }
    then="$(date -d "$ts" +%s 2>/dev/null)" || { printf '%s' "$ts"; return 0; }
    local s=$(($(date +%s) - then))
    if [ "$s" -ge 86400 ]; then
        printf '%dd%dh' $((s / 86400)) $(((s % 86400) / 3600))
    elif [ "$s" -ge 3600 ]; then
        printf '%dh%dm' $((s / 3600)) $(((s % 3600) / 60))
    else
        printf '%dm' $((s / 60))
    fi
}

# ------------------------------------------------------------------ status

svc_status() {
    local s unit act en pp proto port listen
    have systemctl || die "需要 systemd"
    SVC_BAD=0
    printf '== 服务 ==\n'
    for s in $(svc_list "$@"); do
        unit="$(svc_unit "$s")"
        if ! svc_installed "$s"; then
            printf '  %-8s 未安装（bash infra.sh %s）\n' "$s" "$s"
            continue
        fi
        act="$(systemctl is-active "$unit" 2>/dev/null | head -n 1)"
        en="$(systemctl is-enabled "$unit" 2>/dev/null | head -n 1)"
        pp="$(svc_port "$s")"
        if [ -z "$pp" ]; then
            # 没有 TCP/UDP 端口的服务（php-fpm 走 unix socket），只看进程状态
            printf '  %-8s %s' "$s" "$([ "$act" = active ] && echo "${C_GREEN}运行中${C_OFF}" || echo "${C_RED}${act:-未知}${C_OFF}")"
            [ "$act" = active ] || SVC_BAD=$((SVC_BAD + 1))
            printf '  自启:%s  socket: /run/php/php-fpm-web.sock\n' "$([ "$en" = enabled ] && echo 是 || echo "${en:-否}")"
            continue
        fi
        proto="${pp%%/*}"
        port="${pp##*/}"
        listen="$(port_listeners "$proto" "$port")"
        if [ "$act" = "active" ]; then
            printf '  %-8s %s运行中%s' "$s" "$C_GREEN" "$C_OFF"
        else
            printf '  %-8s %s%s%s' "$s" "$C_RED" "${act:-未知}" "$C_OFF"
            SVC_BAD=$((SVC_BAD + 1))
        fi
        printf '  自启:%s' "$([ "$en" = enabled ] && echo 是 || echo "${en:-否}")"
        [ "$act" = "active" ] && printf '  已运行 %s' "$(svc_uptime "$unit")"
        if [ -n "$listen" ]; then
            printf '  %s %s监听%s\n' "$pp" "$C_GREEN" "$C_OFF"
        elif [ "$act" = "active" ]; then
            printf '  %s %s没在监听%s\n' "$pp" "$C_RED" "$C_OFF"
            SVC_BAD=$((SVC_BAD + 1))
        else
            printf '\n'
        fi
    done
    if [ "$SVC_BAD" -eq 0 ]; then
        log "全部正常"
        return 0
    fi
    warn "有 ${SVC_BAD} 项异常（上面标红的）。看日志: bash svc.sh logs <服务>"
    return 1
}

# ------------------------------------------------------------------ start / stop / restart

svc_act() { # <start|stop|restart> [服务...]
    local act="$1" s list ordered=""
    shift
    require_root
    list="$(svc_list "$@")"
    # 启动按依赖顺序（mysql -> radius -> redis -> nginx），停止反过来。
    for s in postgres mysql radius redis php nginx; do
        case " $list " in *" $s "*) ordered="${ordered} ${s}" ;; esac
    done
    if [ "$act" = "stop" ]; then
        ordered="$(printf '%s\n' $ordered | awk '{a[NR]=$0} END{for(i=NR;i>=1;i--) printf "%s ", a[i]}')"
    fi
    for s in $ordered; do
        if ! svc_installed "$s"; then
            warn "${s} 未安装，跳过"
            continue
        fi
        if systemctl "$act" "$(svc_unit "$s")"; then
            log "${act} ${s} 完成"
        else
            err "${act} ${s} 失败: journalctl -u $(svc_unit "$s") -n 30"
            SVC_BAD=$((SVC_BAD + 1))
        fi
    done
    [ "$SVC_BAD" -eq 0 ] || return 1
    [ "$act" = "stop" ] || svc_status "$@"
}

# ------------------------------------------------------------------ check

svc_check() {
    local rc=0 conf="${OPENRESTY_PREFIX:-/usr/local/openresty}/nginx/conf/nginx.conf"
    echo "== nginx 配置语法 =="
    if [ -x /usr/local/openresty/bin/openresty ]; then
        /usr/local/openresty/bin/openresty -t -c "$conf" || rc=1
    else
        echo "  未安装"
    fi
    echo "== mysql 存活 =="
    if have mysqladmin; then
        # ping 即使没有账号权限也会回应，只用来确认进程活着。
        # 8.0 的 root 走 auth_socket，本机 root 直接跑就能过。
        mysqladmin --defaults-file=/dev/null -h 127.0.0.1 -P "$(svc_port mysql | cut -d/ -f2)" ping 2>&1 \
            | head -n 2 || true
    elif [ -x /usr/local/mysql/bin/mysqladmin ]; then
        # 旧版 tarball 安装，没有在 PATH 里。
        /usr/local/mysql/bin/mysqladmin --defaults-file=/dev/null -h 127.0.0.1 -P "$(svc_port mysql | cut -d/ -f2)" ping 2>&1 \
            | head -n 2 || true
    else
        echo "  未安装"
    fi
    echo "== mysql 版本与关键设置 =="
    if have mysql; then
        mysql --defaults-file=/dev/null -e "SELECT VERSION() AS version, @@lower_case_table_names AS lctn, @@character_set_server AS charset, @@sql_mode AS sql_mode\G" 2>&1 | head -20 || true
    fi
    echo "== redis 配置里的绑定与端口 =="
    grep -E '^(bind|port) ' /etc/redis/redis.conf 2>/dev/null || echo "  未安装"
    echo "== radius 进程 =="
    pgrep -a freeradius || echo "  没有 freeradius 进程"
    echo
    svc_status || rc=1
    return "$rc"
}

# ------------------------------------------------------------------ logs / debug

svc_logs() {
    local s="${1:-}" n=100 follow=0 unit
    [ -n "$s" ] || die "用法: svc.sh logs <服务> [-n 行数] [-f]"
    shift
    while [ $# -gt 0 ]; do
        case "$1" in
            -n)
                [ $# -ge 2 ] || die "-n 需要一个行数"
                n="$2"
                shift 2
                ;;
            -f)
                follow=1
                shift
                ;;
            *) die "未知选项: $1" ;;
        esac
    done
    case "$n" in '' | *[!0-9]*) die "-n 必须是数字" ;; esac
    unit="$(svc_unit "$s")" || die "未知服务: ${s}（可选: ${SVC_ALL}）"
    if [ "$follow" -eq 1 ]; then
        journalctl -u "$unit" -n "$n" -f --no-pager
    else
        journalctl -u "$unit" -n "$n" --no-pager
    fi
}

# ------------------------------------------------------------------ 入口

svc_main() {
    local action="${1:-status}"
    [ $# -gt 0 ] && shift
    case "$action" in
        status | '') svc_status "$@" ;;
        start | stop | restart) svc_act "$action" "$@" ;;
        check) svc_check ;;
        logs | log) svc_logs "$@" ;;
        help | -h | --help) svc_usage ;;
        *)
            err "未知动作: ${action}"
            svc_usage
            return 2
            ;;
    esac
}

svc_main "$@"
