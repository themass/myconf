#!/usr/bin/env bash
# 运行状况与日志：一条命令看本机所有已装协议的服务、端口、连接数、近期错误，并按服务查日志。
#
# 用法（通过 vpn.sh 调用）：
#   vpn.sh health                          总览（等同 health status）；有异常时退出码为 1，可接监控
#   vpn.sh health logs [服务...] [选项]     看日志，不写服务名则看全部
#
# 只读：不会启动、停止或修改任何服务和配置。
# 日志来自 systemd journal（Xray / sing-box / strongSwan 都没有单独的日志文件）。

HC_ERR_RE='error|fail|panic|fatal|denied|reject'
HC_WINDOW="${HC_WINDOW:-1 hour ago}"
HC_BAD=0

health_usage() {
    cat <<EOF
运行状况模块:
  status                     总览：系统负载、各服务状态、端口监听、连接数、近期错误（默认动作）
  logs [服务...] [选项]       查看日志

服务名（logs 用）: xray | singbox | wireguard | sync | strongswan | all（默认 all）
  别名: sing-box=singbox  wg=wireguard  wg-sync=sync  ikev2/ipsec=strongswan

logs 选项:
  -n <行数>        显示最后多少行，默认 100
  -f               持续跟踪新日志（Ctrl-C 退出）
  --since <时间>   只看这段时间之后的，如 '30 min ago'、'2026-11-09 10:00'
  -e, --errors     只看含 error / fail / panic / fatal / denied / reject 的行
  --raw            不打码。默认会把 UUID、44 位密钥、32 位以上的十六进制串打码，方便贴给别人看

环境变量:
  HC_WINDOW        status 里统计"近期错误"的时间窗口，默认 "1 hour ago"

示例:
  bash vpn.sh health
  bash vpn.sh health logs xray -n 50
  bash vpn.sh health logs strongswan sing-box -f
  bash vpn.sh health logs --errors --since '30 min ago'

退出码: status 全部正常为 0，有服务未运行 / 端口未监听 / 同步任务失败为 1。
EOF
}

# ------------------------------------------------------------------ 小工具

hc_prop() { # <unit> <属性>
    systemctl show -p "$2" "$1" 2>/dev/null | head -n 1 | cut -d= -f2-
}

hc_duration() { # <秒> -> 3d4h / 5h12m / 7m
    local s="$1" d h m
    [ "$s" -ge 0 ] 2>/dev/null || { printf -- '-'; return 0; }
    d=$((s / 86400))
    h=$(((s % 86400) / 3600))
    m=$(((s % 3600) / 60))
    if [ "$d" -gt 0 ]; then
        printf '%dd%dh' "$d" "$h"
    elif [ "$h" -gt 0 ]; then
        printf '%dh%dm' "$h" "$m"
    else
        printf '%dm' "$m"
    fi
}

hc_uptime() { # <unit>
    local ts then now
    ts="$(hc_prop "$1" ActiveEnterTimestamp)"
    [ -n "$ts" ] || { printf -- '-'; return 0; }
    then="$(date -d "$ts" +%s 2>/dev/null)" || { printf '%s' "$ts"; return 0; }
    now="$(date +%s)"
    hc_duration $((now - then))
}

# 公网端口会被扫描器随机探测，sing-box 对这类连接会打 ERROR（坏请求、TLS 握手 EOF、路径不对）。
# 这些不代表服务有问题，总览的计数里排除掉，否则数字永远虚高；health logs --errors 仍然全部显示。
HC_NOISE_RE='bad request|bad path|TLS handshake: EOF'

hc_errors() { # <unit> -> 近期错误行数（已排除连接噪音）
    have journalctl || { printf '?'; return 0; }
    journalctl -u "$1" --since "$HC_WINDOW" --no-pager -q -o cat 2>/dev/null \
        | grep -iE "$HC_ERR_RE" | grep -viE "$HC_NOISE_RE" | wc -l | tr -d ' '
}

hc_strongswan_unit() {
    local u
    for u in strongswan strongswan-starter strongswan-swanctl ipsec; do
        if systemctl cat "$u" >/dev/null 2>&1; then
            printf '%s' "$u"
            return 0
        fi
    done
    return 1
}

# 是否装了：单元存在，并且配置文件在（wg-quick@ 是模板单元，装了 wireguard-tools 就存在，不能只看单元）
hc_installed() { # <类型> <unit>
    case "$1" in
        wireguard) [ -f "/etc/wireguard/${WG_IF:-wg0}.conf" ] && systemctl cat "$2" >/dev/null 2>&1 ;;
        wgsync) [ -f /etc/wireguard/sync.env ] && systemctl cat "$2" >/dev/null 2>&1 ;;
        *) systemctl cat "$2" >/dev/null 2>&1 ;;
    esac
}

# ------------------------------------------------------------------ 系统

hc_system() {
    printf '== 系统 ==\n'
    printf '  负载:%s' "$(uptime | sed -E 's/.*load averages?: *//')"
    if have free; then
        free -m | awk '/^Mem:/{printf "   内存: %d/%dM", $3, $2} /^Swap:/{printf "   swap: %d/%dM", $3, $2}'
    fi
    df -P / 2>/dev/null | awk 'NR==2{printf "   磁盘 /: %s", $5}'
    printf '\n'
}

# ------------------------------------------------------------------ 端口

# hc_port <标签> <tcp|udp> <端口>：打印一行监听情况，没监听记一项异常。
hc_port() {
    local label="$1" proto="$2" port="$3" out conns=""
    [ -n "$port" ] || return 0
    out="$(port_listeners "$proto" "$port")"
    if [ -n "$out" ]; then
        if [ "$proto" = "tcp" ] && have ss; then
            conns="$(ss -tn state established "( sport = :${port} )" 2>/dev/null | tail -n +2 | wc -l | tr -d ' ')"
            printf '      %-14s %s/%-6s %s监听%s  已建立连接 %s\n' "$label" "$proto" "$port" "$C_GREEN" "$C_OFF" "$conns"
        else
            printf '      %-14s %s/%-6s %s监听%s\n' "$label" "$proto" "$port" "$C_GREEN" "$C_OFF"
        fi
    else
        printf '      %-14s %s/%-6s %s未监听%s\n' "$label" "$proto" "$port" "$C_RED" "$C_OFF"
        HC_BAD=$((HC_BAD + 1))
    fi
}

hc_xray_port() {
    local cfg="${XRAY_CONFIG_DIR:-/usr/local/etc/xray}/config.json" p=""
    [ -f "$cfg" ] && p="$(grep -o '"port"[[:space:]]*:[[:space:]]*[0-9]*' "$cfg" | head -n 1 | grep -o '[0-9]*$')"
    printf '%s' "${p:-${XRAY_PORT:-443}}"
}

hc_singbox_ports() {
    local dir="${SB_ETC:-/etc/sing-box}/state" f p port
    [ -d "$dir" ] || return 0
    for f in "$dir"/*.env; do
        [ -f "$f" ] || continue
        p="$(basename "$f" .env)"
        port="$(grep '^PORT=' "$f" | head -n 1 | cut -d= -f2-)"
        case "$p" in
            hysteria2) hc_port "$p" udp "$port" ;;
            shadowsocks)
                hc_port "$p" tcp "$port"
                hc_port "$p" udp "$port"
                ;;
            *) hc_port "$p" tcp "$port" ;;
        esac
    done
}

# ------------------------------------------------------------------ 各服务的细节

hc_detail_xray() {
    hc_port "vless-reality" tcp "$(hc_xray_port)"
}

hc_detail_singbox() {
    hc_singbox_ports
}

hc_detail_wireguard() {
    local wgif="${WG_IF:-wg0}" port dump now total=0 fresh=0 line pk psk ep ips hs rx tx ka
    have wg || return 0
    port="$(wg show "$wgif" listen-port 2>/dev/null)"
    if [ -n "$port" ]; then
        hc_port "$wgif" udp "$port"
    else
        printf '      %-14s %s接口不存在%s\n' "$wgif" "$C_RED" "$C_OFF"
        HC_BAD=$((HC_BAD + 1))
        return 0
    fi
    now="$(date +%s)"
    dump="$(wg show "$wgif" dump 2>/dev/null | tail -n +2)"
    if [ -n "$dump" ]; then
        while IFS= read -r line; do
            [ -n "$line" ] || continue
            total=$((total + 1))
            IFS=$'\t' read -r pk psk ep ips hs rx tx ka <<<"$line"
            if [ "${hs:-0}" -gt 0 ] 2>/dev/null && [ $((now - hs)) -lt 180 ]; then
                fresh=$((fresh + 1))
            fi
        done <<<"$dump"
    fi
    printf '      设备 %s 台，近 3 分钟有握手 %s 台\n' "$total" "$fresh"
}

hc_detail_wgsync() {
    local level last result
    level="$(grep '^WG_SYNC_LEVEL=' /etc/wireguard/sync.env 2>/dev/null | head -n 1 | cut -d= -f2-)"
    last="$(hc_prop wg-sync.service ExecMainExitTimestamp)"
    result="$(hc_prop wg-sync.service Result)"
    printf '      线路等级 %s；上次同步 %s（%s）\n' "${level:-?}" "${last:-还没有运行过}" "${result:--}"
    if [ "$(systemctl is-failed wg-sync.service 2>/dev/null)" = "failed" ]; then
        printf '      %s同步任务上次失败%s，看: bash vpn.sh health logs sync\n' "$C_RED" "$C_OFF"
        HC_BAD=$((HC_BAD + 1))
    fi
}

hc_detail_strongswan() {
    local ports p sas=""
    have ss || return 0
    ports="$(ss -lunp 2>/dev/null | tail -n +2 | grep charon | awk '{print $4}' | sed 's/.*://' | sort -un | tr '\n' ' ')"
    if [ -z "$ports" ]; then
        printf '      %-14s %s没有看到 charon 在监听 udp%s（非 root 时看不到进程名）\n' "ikev2" "$C_RED" "$C_OFF"
        HC_BAD=$((HC_BAD + 1))
    else
        for p in $ports; do
            hc_port "ikev2" udp "$p"
        done
    fi
    if have swanctl; then
        sas="$(swanctl --list-sas 2>/dev/null | grep -c ESTABLISHED || true)"
    elif have ipsec; then
        sas="$(ipsec statusall 2>/dev/null | grep -c ESTABLISHED || true)"
    fi
    [ -n "$sas" ] && printf '      当前 IKE 连接 %s 个\n' "$sas"
}

# ------------------------------------------------------------------ status

hc_service() { # <名称> <unit> <类型>
    local name="$1" unit="$2" kind="$3" act en up rs er
    act="$(systemctl is-active "$unit" 2>/dev/null | head -n 1)"
    en="$(systemctl is-enabled "$unit" 2>/dev/null | head -n 1)"
    # 只有运行中才有"已运行多久"；停止后 ActiveEnterTimestamp 还是上次启动的旧值，会误导人
    if [ "$act" = "active" ]; then up="$(hc_uptime "$unit")"; else up="-"; fi
    rs="$(hc_prop "$unit" NRestarts)"
    er="$(hc_errors "$unit")"
    if [ "$act" = "active" ]; then
        printf '  %-12s %s运行中%s' "$name" "$C_GREEN" "$C_OFF"
    else
        printf '  %-12s %s%s%s' "$name" "$C_RED" "${act:-未知}" "$C_OFF"
        HC_BAD=$((HC_BAD + 1))
    fi
    case "$en" in
        enabled | static) printf '  自启:是' ;;
        *) printf '  %s自启:%s%s' "$C_YELLOW" "${en:-否}" "$C_OFF" ;;
    esac
    printf '  已运行 %s  重启 %s 次  近期错误 %s\n' "$up" "${rs:--}" "${er:-0}"
    # 服务没在运行时不再看端口，免得一个故障刷出一排"未监听"
    [ "$act" = "active" ] && "hc_detail_${kind}"
    return 0
}

health_status() {
    local entry name unit kind missing=""
    have systemctl || die "需要 systemd（systemctl）"
    HC_BAD=0
    hc_system
    printf '== 服务（"近期错误"统计窗口: %s）==\n' "$HC_WINDOW"
    for entry in "xray|xray|xray" "sing-box|sing-box|singbox" "wireguard|wg-quick@${WG_IF:-wg0}|wireguard" \
        "wg-sync|wg-sync.timer|wgsync" "strongswan|@strongswan|strongswan"; do
        IFS='|' read -r name unit kind <<<"$entry"
        if [ "$unit" = "@strongswan" ]; then
            unit="$(hc_strongswan_unit)" || {
                missing="${missing} ${name}"
                continue
            }
        fi
        if hc_installed "$kind" "$unit"; then
            hc_service "$name" "$unit" "$kind"
        else
            missing="${missing} ${name}"
        fi
    done
    [ -n "$missing" ] && printf '  未安装（已跳过）:%s\n' "$missing"
    printf '\n'
    if [ "$HC_BAD" -eq 0 ]; then
        log "全部正常"
        printf '看日志: bash vpn.sh health logs <服务> [-f]    详细说明: bash vpn.sh health help\n'
        return 0
    fi
    warn "有 ${HC_BAD} 项异常（上面标红的）。看日志: bash vpn.sh health logs <服务> --errors"
    return 1
}

# ------------------------------------------------------------------ logs

# 服务名 -> unit（可能多个，空格分隔）。未知服务返回 1。
hc_log_unit() {
    local u
    case "$1" in
        xray) printf 'xray' ;;
        singbox | sing-box) printf 'sing-box' ;;
        wireguard | wg) printf 'wg-quick@%s' "${WG_IF:-wg0}" ;;
        sync | wg-sync) printf 'wg-sync.service' ;;
        strongswan | ikev2 | ipsec)
            u="$(hc_strongswan_unit)" || return 1
            printf '%s' "$u"
            ;;
        all)
            for u in xray sing-box "wg-quick@${WG_IF:-wg0}" wg-sync.service "$(hc_strongswan_unit)"; do
                [ -n "$u" ] && systemctl cat "$u" >/dev/null 2>&1 && printf '%s ' "$u"
            done
            ;;
        *) return 1 ;;
    esac
}

# 打码：UUID 留前 8 位；44 位 Base64 密钥；32 位以上十六进制串。
hc_mask() {
    sed -E \
        -e 's#([0-9a-fA-F]{8})-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}#\1-****#g' \
        -e 's#[A-Za-z0-9+/]{43}=#<key>#g' \
        -e 's#[0-9a-fA-F]{32,}#<hex>#g'
}

health_logs() {
    local n=100 follow=0 since="" errors=0 raw=0 units="" u a
    local args
    have journalctl || die "需要 systemd journal（journalctl）"
    while [ $# -gt 0 ]; do
        case "$1" in
            -n)
                [ $# -ge 2 ] || die "-n 需要一个行数"
                n="$2"
                shift 2
                ;;
            -f | --follow)
                follow=1
                shift
                ;;
            --since)
                [ $# -ge 2 ] || die "--since 需要一个时间，如 '30 min ago'"
                since="$2"
                shift 2
                ;;
            -e | --errors)
                errors=1
                shift
                ;;
            --raw)
                raw=1
                shift
                ;;
            -h | --help | help)
                health_usage
                return 0
                ;;
            -*) die "未知选项: $1（health help 查看用法）" ;;
            *)
                u="$(hc_log_unit "$1")" || die "未知或未安装的服务: $1（可选: xray singbox wireguard sync strongswan all）"
                units="${units} ${u}"
                shift
                ;;
        esac
    done
    case "$n" in '' | *[!0-9]*) die "-n 必须是数字" ;; esac
    [ -n "$units" ] || units="$(hc_log_unit all)"
    [ -n "$units" ] || die "没有发现任何已安装的服务"

    args=(--no-pager -o short-iso -n "$n")
    for a in $units; do
        args+=(-u "$a")
    done
    [ -n "$since" ] && args+=(--since "$since")
    [ "$follow" -eq 1 ] && args+=(-f)

    if [ "$errors" -eq 1 ] && [ "$raw" -eq 1 ]; then
        journalctl "${args[@]}" | grep --line-buffered -iE "$HC_ERR_RE"
    elif [ "$errors" -eq 1 ]; then
        journalctl "${args[@]}" | grep --line-buffered -iE "$HC_ERR_RE" | hc_mask
    elif [ "$raw" -eq 1 ]; then
        journalctl "${args[@]}"
    else
        journalctl "${args[@]}" | hc_mask
    fi
}

# ------------------------------------------------------------------ 入口

health_main() {
    local action="${1:-status}"
    [ $# -gt 0 ] && shift
    case "$action" in
        status | '') health_status "$@" ;;
        logs | log) health_logs "$@" ;;
        help | -h | --help) health_usage ;;
        *)
            err "未知动作: ${action}"
            health_usage
            return 2
            ;;
    esac
}
