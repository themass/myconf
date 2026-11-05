#!/usr/bin/env bash
# VPN 服务端安装统一入口。
#
#   bash vpn.sh <模块> <动作> [参数...]
#   bash vpn.sh ports | links | help
#
# 模块: system strongswan ssr xray singbox wireguard
# 每个模块 `bash vpn.sh <模块> help` 查看动作和环境变量。

if [ -z "${BASH_VERSION:-}" ]; then
    if command -v bash >/dev/null 2>&1; then
        exec bash "$0" "$@"
    fi
    echo "需要 bash: bash $0 ..." >&2
    exit 2
fi

VPN_SHELL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export VPN_SHELL_DIR
# shellcheck source=lib/common.sh
source "${VPN_SHELL_DIR}/lib/common.sh"

VPN_MODULES="system strongswan ssr xray singbox wireguard"

usage() {
    cat <<EOF
用法: bash vpn.sh <模块> <动作> [参数...]

模块:
  system      依赖、内核参数、BBR、IPsec NAT、监控、诊断
  strongswan  IKEv2/IPsec（5.9 的 ipsec.conf 版 和 6.x 的 swanctl 版）
  ssr         ShadowsocksR / ss-panel
  xray        Xray VLESS+Reality（TCP 443）
  singbox     sing-box: vless-reality / vmess-ws / trojan / shadowsocks / hysteria2
  wireguard   WireGuard

其他:
  ports       各协议默认端口，以及本机当前的监听情况
  links       输出已安装的 Xray / sing-box / WireGuard 的客户端信息
  help        本说明

示例:
  bash vpn.sh xray install
  bash vpn.sh singbox add all
  bash vpn.sh wireguard install && bash vpn.sh wireguard add-peer phone
  bash vpn.sh strongswan all

配置模板在 ${TEMPLATE_DIR}（复制修改，不要写进脚本）。
服务器地址和出口网卡自动识别；识别不对时设置 SERVER_ADDRESS / VPN_NETDEV。
EOF
}

show_ports() {
    cat <<'EOF'
默认端口（同机共存，互不冲突）:
  strongSwan 默认版      udp 500, 4500
  strongSwan 端口版      udp 8081 (IKE), 8080 (NAT-T)
  Xray VLESS+Reality     tcp 443            XRAY_PORT
  sing-box VLESS+Reality tcp 444            SB_VLESS_PORT
  sing-box Trojan        tcp 8443           SB_TROJAN_PORT
  sing-box VMess+WS      tcp 8880           SB_VMESS_PORT
  sing-box Shadowsocks   tcp+udp 8388       SB_SS_PORT
  sing-box Hysteria2     udp 8444           SB_HY2_PORT
  WireGuard              udp 51820          WG_PORT

本机当前监听:
EOF
    if have ss; then
        ss -lntup 2>/dev/null | grep -E 'charon|xray|sing-box|wg|ssserver|python' || echo "  (没有相关进程在监听)"
    else
        echo "  (没有 ss 命令)"
    fi
}

show_links() {
    local shown=0
    if [ -f "${XRAY_CONFIG_DIR:-/usr/local/etc/xray}/config.json" ]; then
        # shellcheck source=modules/xray.sh
        source "${VPN_SHELL_DIR}/modules/xray.sh"
        echo "== Xray =="
        xray_links || true
        shown=1
    fi
    if [ -d /etc/sing-box/state ]; then
        # shellcheck source=modules/singbox.sh
        source "${VPN_SHELL_DIR}/modules/singbox.sh"
        echo "== sing-box =="
        sb_links
        shown=1
    fi
    if [ -f /etc/wireguard/server.pub ]; then
        # shellcheck source=modules/wireguard.sh
        source "${VPN_SHELL_DIR}/modules/wireguard.sh"
        echo "== WireGuard =="
        wg_info
        shown=1
    fi
    [ "$shown" -eq 1 ] || echo "没有发现已安装的 Xray / sing-box / WireGuard"
}

main() {
    local mod="${1:-}"
    [ $# -gt 0 ] && shift
    case "$mod" in
        '' | help | -h | --help)
            usage
            ;;
        ports)
            show_ports
            ;;
        links)
            show_links
            ;;
        system | strongswan | ssr | xray | singbox | wireguard)
            # shellcheck disable=SC1090
            source "${VPN_SHELL_DIR}/modules/${mod}.sh"
            "${mod}_main" "$@"
            ;;
        *)
            err "未知模块: ${mod}"
            usage
            exit 2
            ;;
    esac
}

main "$@"
