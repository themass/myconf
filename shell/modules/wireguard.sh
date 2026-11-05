#!/usr/bin/env bash
# WireGuard 服务端。
#
# 用法（通过 vpn.sh 调用）：
#   vpn.sh wireguard install
#   vpn.sh wireguard add-peer <名字> [客户端公钥]   给了公钥就只登记（App 自己生成密钥）；
#                                                   不给就生成整套客户端配置
#   vpn.sh wireguard del-peer <名字>
#   vpn.sh wireguard list | info | status | restart | uninstall
#
# 文件布局（/etc/wireguard）：
#   server.key / server.pub     服务端密钥
#   wg0.base.conf               [Interface] 段，由 templates/wireguard/wg0.base.conf 渲染
#   peers.d/<名字>.conf          每个客户端一个 [Peer] 段
#   wg0.conf                    = wg0.base.conf + peers.d/*.conf，每次增删后重新生成
# wg-quick 不支持 include，所以拼接成完整的 wg0.conf；运行中的接口用 syncconf 热更新，不断开已有连接。

WG_IF="${WG_IF:-wg0}"
WG_ETC="${WG_ETC:-/etc/wireguard}"
WG_PORT="${WG_PORT:-51820}"
WG_SUBNET="${WG_SUBNET:-10.66.66.0/24}"
WG_DNS="${WG_DNS:-1.1.1.1}"
WG_MTU="${WG_MTU:-1420}"
WG_PEERS="${WG_ETC}/peers.d"

wireguard_usage() {
    cat <<EOF
WireGuard 模块:
  install                        安装 wireguard-tools，生成服务端密钥，启动 ${WG_IF}
  add-peer <名字> [客户端公钥]   登记客户端；不给公钥则生成密钥并输出完整客户端配置
  del-peer <名字>                删除客户端
  list                           列出客户端和分配的地址
  info                           服务端公钥、端点、网段（填后端/客户端用）
  status                         wg show
  restart                        重新生成 wg0.conf 并重启接口
  uninstall                      停止并禁用接口（WG_PURGE=1 同时删除 ${WG_ETC} 下的配置）

环境变量:
  WG_PORT         监听端口，默认 51820/udp
  WG_SUBNET       内网网段，必须是 /24，默认 10.66.66.0/24（服务端占 .1）
  WG_DNS / WG_MTU 生成客户端配置时使用，默认 1.1.1.1 / 1420
  VPN_NETDEV      出口网卡（默认自动识别默认路由所在网卡）
  SERVER_ADDRESS  服务器公网地址（默认自动识别）
EOF
}

# ------------------------------------------------------------------ 网段

# 把 WG_SUBNET 拆成三段前缀，如 10.66.66。只支持 /24，够用且分配逻辑最简单。
wg_prefix() {
    case "$WG_SUBNET" in
        *.*.*.0/24) printf '%s\n' "${WG_SUBNET%.0/24}" ;;
        *) die "WG_SUBNET 必须形如 10.66.66.0/24，当前: ${WG_SUBNET}" ;;
    esac
}

wg_server_ip() { printf '%s.1\n' "$(wg_prefix)"; }

wg_valid_name() {
    case "$1" in
        '' | *[!A-Za-z0-9_-]*) return 1 ;;
    esac
    return 0
}

wg_valid_pubkey() {
    # WireGuard 公钥是 32 字节的 base64：44 个字符，以 = 结尾。
    [[ "$1" =~ ^[A-Za-z0-9+/]{43}=$ ]]
}

# 下一个空闲地址（.2 起），已被占用的从 peers.d 里读。
wg_next_ip() {
    local prefix n used
    prefix="$(wg_prefix)"
    used="$(cat "${WG_PEERS}"/*.conf 2>/dev/null | sed -n "s/^AllowedIPs = ${prefix//./\\.}\.\([0-9]*\)\/32.*/\1/p")"
    for ((n = 2; n <= 254; n++)); do
        if ! printf '%s\n' "$used" | grep -qx "$n"; then
            printf '%s.%s\n' "$prefix" "$n"
            return 0
        fi
    done
    return 1
}

# ------------------------------------------------------------------ 配置生成

wg_rebuild() {
    local conf="${WG_ETC}/${WG_IF}.conf" tmp
    tmp="$(mktemp "${WG_ETC}/.wgconf.XXXXXX")" || die "无法在 ${WG_ETC} 创建临时文件"
    chmod 600 "$tmp"
    cat "${WG_ETC}/${WG_IF}.base.conf" >"$tmp"
    if ls "${WG_PEERS}"/*.conf >/dev/null 2>&1; then
        cat "${WG_PEERS}"/*.conf >>"$tmp"
    fi
    mv -f "$tmp" "$conf"
}

# 接口已经起来就热更新；没起来就启动。
wg_apply() {
    wg_rebuild
    if ip link show "$WG_IF" >/dev/null 2>&1; then
        wg syncconf "$WG_IF" <(wg-quick strip "$WG_IF") || die "wg syncconf 失败"
    else
        systemctl enable "wg-quick@${WG_IF}" >/dev/null 2>&1 || true
        systemctl restart "wg-quick@${WG_IF}" || die "启动 ${WG_IF} 失败: journalctl -u wg-quick@${WG_IF}"
    fi
}

wg_endpoint() {
    local addr
    addr="$(detect_server_address)" || die "无法识别服务器地址，请设置 SERVER_ADDRESS"
    printf '%s:%s\n' "$addr" "$WG_PORT"
}

# ------------------------------------------------------------------ 动作

wg_install() {
    require_root
    have systemctl || die "需要 systemd"
    ensure_cmds wg:wireguard-tools iptables ip:iproute2
    assert_port_free udp "$WG_PORT" "" WG_PORT

    local netdev
    netdev="$(get_netdev)"
    mkdir -p "$WG_PEERS"
    chmod 700 "$WG_ETC" "$WG_PEERS"

    if [ ! -f "${WG_ETC}/server.key" ]; then
        (
            umask 077
            wg genkey >"${WG_ETC}/server.key"
        )
        wg pubkey <"${WG_ETC}/server.key" >"${WG_ETC}/server.pub"
        log "已生成服务端密钥"
    fi

    enable_ip_forward
    install_template "${TEMPLATE_DIR}/wireguard/wg0.base.conf" "${WG_ETC}/${WG_IF}.base.conf" 600 \
        "SERVER_ADDRESS=$(wg_server_ip)" "PORT=${WG_PORT}" "SUBNET=${WG_SUBNET}" \
        "NETDEV=${netdev}" "PRIVATE_KEY=$(cat "${WG_ETC}/server.key")"

    open_port udp "$WG_PORT"
    wg_apply
    remind_security_group
    log "WireGuard 已启动: ${WG_IF}，出口网卡 ${netdev}"
    wg_info
}

wg_info() {
    [ -f "${WG_ETC}/server.pub" ] || die "尚未安装，先运行: vpn.sh wireguard install"
    echo "服务端公钥: $(cat "${WG_ETC}/server.pub")"
    echo "端点:       $(wg_endpoint)"
    echo "网段:       ${WG_SUBNET}（服务端 $(wg_server_ip)）"
}

wg_add_peer() {
    local name="${1:-}" pubkey="${2:-}" ip client_priv="" tmp
    require_root
    wg_valid_name "$name" || die "用法: vpn.sh wireguard add-peer <名字(字母数字_-)> [客户端公钥]"
    [ -f "${WG_ETC}/server.pub" ] || die "尚未安装，先运行: vpn.sh wireguard install"
    [ ! -f "${WG_PEERS}/${name}.conf" ] || die "客户端 ${name} 已存在，先 del-peer 或换个名字"

    if [ -n "$pubkey" ]; then
        wg_valid_pubkey "$pubkey" || die "公钥格式不对（应为 44 位 base64，以 = 结尾）"
        grep -qs "^PublicKey = ${pubkey}\$" "${WG_PEERS}"/*.conf && die "这个公钥已经登记过"
    else
        client_priv="$(wg genkey)"
        pubkey="$(printf '%s' "$client_priv" | wg pubkey)"
    fi

    ip="$(wg_next_ip)" || die "地址池已满（${WG_SUBNET}）"
    install_template "${TEMPLATE_DIR}/wireguard/peer.conf" "${WG_PEERS}/${name}.conf" 600 \
        "NAME=${name}" "PUBLIC_KEY=${pubkey}" "PEER_ADDRESS=${ip}"
    wg_apply

    log "已添加 ${name}，地址 ${ip}"
    if [ -n "$client_priv" ]; then
        echo "---------- 客户端配置（保存为 ${name}.conf，私钥只显示这一次）----------"
        tmp="$(mktemp "${TMPDIR:-/tmp}/wg-client.XXXXXX")"
        render_template "${TEMPLATE_DIR}/wireguard/client.conf" "$tmp" \
            "CLIENT_PRIVATE_KEY=${client_priv}" "PEER_ADDRESS=${ip}" "DNS=${WG_DNS}" "MTU=${WG_MTU}" \
            "SERVER_PUBLIC_KEY=$(cat "${WG_ETC}/server.pub")" "ENDPOINT=$(wg_endpoint)" \
            "ALLOWED_IPS=0.0.0.0/0"
        cat "$tmp"
        if have qrencode; then
            echo "---------- 二维码 ----------"
            qrencode -t ansiutf8 <"$tmp"
        fi
        rm -f "$tmp"
    else
        echo "客户端地址 (clientAddress): ${ip}/32"
        echo "服务端公钥 (peerPublicKey): $(cat "${WG_ETC}/server.pub")"
        echo "端点:                       $(wg_endpoint)"
    fi
}

wg_del_peer() {
    local name="${1:-}"
    require_root
    wg_valid_name "$name" || die "用法: vpn.sh wireguard del-peer <名字>"
    [ -f "${WG_PEERS}/${name}.conf" ] || die "没有这个客户端: ${name}"
    rm -f "${WG_PEERS}/${name}.conf"
    wg_apply
    log "已删除 ${name}"
}

wg_list() {
    local f name ip
    ls "${WG_PEERS}"/*.conf >/dev/null 2>&1 || {
        echo "(没有客户端)"
        return 0
    }
    for f in "${WG_PEERS}"/*.conf; do
        name="$(basename "$f" .conf)"
        ip="$(sed -n 's/^AllowedIPs = \(.*\)$/\1/p' "$f" | head -n 1)"
        printf '%-20s %s\n' "$name" "$ip"
    done
}

wg_status() {
    wg show "$WG_IF" 2>/dev/null || echo "${WG_IF} 未运行"
}

wg_restart() {
    require_root
    wg_rebuild
    systemctl restart "wg-quick@${WG_IF}" || die "重启失败: journalctl -u wg-quick@${WG_IF}"
}

wg_uninstall() {
    require_root
    systemctl stop "wg-quick@${WG_IF}" 2>/dev/null || true
    systemctl disable "wg-quick@${WG_IF}" 2>/dev/null || true
    if [ "${WG_PURGE:-0}" = "1" ]; then
        rm -rf "$WG_ETC"
        log "已停止并删除 ${WG_ETC}"
    else
        log "已停止；配置和密钥保留在 ${WG_ETC}（WG_PURGE=1 可一并删除）"
    fi
}

wireguard_main() {
    local action="${1:-}"
    [ $# -gt 0 ] && shift
    case "$action" in
        install) wg_install ;;
        add-peer) wg_add_peer "$@" ;;
        del-peer) wg_del_peer "$@" ;;
        list) wg_list ;;
        info) wg_info ;;
        status) wg_status ;;
        restart) wg_restart ;;
        uninstall) wg_uninstall ;;
        '' | help | -h | --help) wireguard_usage ;;
        *)
            err "未知动作: ${action}"
            wireguard_usage
            return 2
            ;;
    esac
}
