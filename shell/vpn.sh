#!/usr/bin/env bash
# VPN 服务端安装统一入口。
#
#   bash vpn.sh <模块> <动作> [参数...]
#   bash vpn.sh ports | links | help
#
# 模块: system strongswan ssr xray singbox wireguard postgres health
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

VPN_MODULES="system strongswan ssr xray singbox wireguard postgres health"

usage() {
    cat <<EOF
用法: bash vpn.sh <模块> <动作> [参数...]

模块与全部动作（每个动作的参数和环境变量: bash vpn.sh help <模块>）:

  system      服务器准备
      init | upgrade [full] [dry-run] | net | bbr | iptables-ipsec | fail2ban
      rclocal | speed | trace | kernel-check | ip
  strongswan  IKEv2/IPsec（strongSwan 6.x，swanctl + vici）
      all | install | config | config-port | ca | fix | check | clean [force] | status
  xray        VLESS+Reality（tcp 443）
      install | upgrade | regen | links | check | status | restart
  singbox     vmess-ws / trojan / shadowsocks / hysteria2（vless-reality 由 xray 承载）
      install | add <协议|all> | remove <协议> | links | sql [行id] | status | check | restart
      upgrade | uninstall
  wireguard   WireGuard（内网 10.66.0.0/16）
      install | sync-install | sync | add-peer <名> | del-peer <名> | list | info | status
      restart | uninstall
  ssr         ShadowsocksR / ss-panel
      install | sspanel
  postgres    PostgreSQL（安装、启停、超级用户、业务库；说明见 docs/postgres.md）
      setup | install | roles | db | start | stop | restart | status | check
  health      运行状况总览和日志（只读）
      status（默认） | logs [服务...] [-n N] [-f] [--since T] [--errors] [--raw]

其他:
  ports       各协议默认端口，以及本机当前的监听情况
  links       输出已安装的 Xray / sing-box / WireGuard 的客户端信息
  help        本说明；help <模块> 看某个模块；help all 看全部模块的详细说明

常用场景:
  新机器从零装全:
      bash vpn.sh system init && bash vpn.sh system net && bash vpn.sh system bbr
      bash vpn.sh xray install
      bash vpn.sh singbox add all
      bash vpn.sh wireguard install
      bash vpn.sh strongswan all
  升级系统包:
      bash vpn.sh system upgrade dry-run      # 先看会升级什么
      bash vpn.sh system upgrade              # 执行（不自动重启服务）
      bash vpn.sh health                      # 升级后确认服务都在
  日常查看:
      bash vpn.sh health                      # 服务、端口、连接数、近期错误
      bash vpn.sh health logs xray -f         # 跟踪某个服务的日志
      bash vpn.sh links                       # 导出客户端链接
  写入后端节点列表:
      bash vpn.sh singbox sql <host_v2 行 id> # 打印 UPDATE 语句
      bash vpn.sh wireguard info              # 取服务端公钥（peerPublicKey）

全局环境变量（识别错了才需要设）:
  SERVER_ADDRESS   服务器公网地址（默认自动识别）
  VPN_NETDEV       出口网卡（默认取默认路由所在网卡，不用再手改网卡名）
  VPN_TEMPLATE_DIR 配置模板目录（默认 ${TEMPLATE_DIR}）
  NO_COLOR=1       关闭彩色输出

配置模板在 ${TEMPLATE_DIR}（复制修改，不要写进脚本）。
EOF
}

# help [模块|all]：不带参数是总览；带模块名看该模块的完整说明；all 依次打印所有模块。
# 每个模块在子 shell 里加载，互相的函数和变量不会串。
show_help() {
    local target="${1:-}" m
    case "$target" in
        '')
            usage
            ;;
        all)
            usage
            for m in $VPN_MODULES; do
                printf '\n==================== %s ====================\n' "$m"
                (
                    # shellcheck disable=SC1090
                    source "${VPN_SHELL_DIR}/modules/${m}.sh"
                    "${m}_main" help
                )
            done
            ;;
        *)
            case " $VPN_MODULES " in
                *" $target "*)
                    (
                        # shellcheck disable=SC1090
                        source "${VPN_SHELL_DIR}/modules/${target}.sh"
                        "${target}_main" help
                    )
                    ;;
                *)
                    err "没有这个模块: ${target}（可选: ${VPN_MODULES}）"
                    return 2
                    ;;
            esac
            ;;
    esac
}

show_ports() {
    cat <<'EOF'
默认端口（同机共存，互不冲突）:
  strongSwan            udp 8081 (IKE), 8080 (NAT-T)   SS_IKE_PORT / SS_NATT_PORT
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
        '')
            usage
            ;;
        help | -h | --help)
            show_help "$@"
            ;;
        ports)
            show_ports
            ;;
        links)
            show_links
            ;;
        system | strongswan | ssr | xray | singbox | wireguard | postgres | health)
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
