#!/usr/bin/env bash
# FreeRADIUS 的日常操作：更新 clients.conf、启停、调试、状态。
# 取代旧的 radiusd.sh（start/stop/debug）和 init_radius_client（替换 clients.conf 并重启）。
# 安装见 infra.sh radius；sql 模块（数据库连接）只在安装时写一次。
#
#   bash radius.sh clients           用 conf/radius/clients.conf 替换线上的，校验通过后重启；失败自动还原
#   bash radius.sh start | stop | restart | status
#   bash radius.sh debug             停掉服务，前台运行 radiusd -X 看日志（Ctrl-C 后用 start 恢复）
#   bash radius.sh check             只做配置语法检查，不改任何东西
#
# clients.conf 含各 NAS 的共享密钥，权限 640、属组 freerad，不写进日志。

if [ -z "${BASH_VERSION:-}" ]; then
    command -v bash >/dev/null 2>&1 && exec bash "$0" "$@"
    echo "需要 bash: bash $0 ..." >&2
    exit 2
fi

VPN_SHELL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export VPN_SHELL_DIR
# shellcheck source=lib/common.sh
source "${VPN_SHELL_DIR}/lib/common.sh"

# 配置目录随包版本不同：Ubuntu 3.0.x 在 /etc/freeradius/3.0，
# NetworkRadius 3.2.10 在 /etc/freeradius。有 mods-available 的那层才是配置根。
radius_etc_dir() {
    local d
    for d in "${RADIUS_ETC:-}" /etc/freeradius/3.0 /etc/freeradius; do
        [ -n "$d" ] && [ -d "${d}/mods-available" ] && { printf '%s\n' "$d"; return 0; }
    done
    return 1
}
RADIUS_ETC="$(radius_etc_dir)" || RADIUS_ETC="${RADIUS_ETC:-/etc/freeradius}"
RADIUS_UNIT=freeradius
RADIUS_SRC="${MYCONF_HOME}/conf/radius/clients.conf"

radius_usage() {
    cat <<EOF
用法: bash radius.sh <动作>

  clients   用 ${RADIUS_SRC} 替换线上的 ${RADIUS_ETC}/clients.conf。
            先备份旧文件，语法检查通过才重启；检查不过就还原旧文件，服务保持原样。
  start     启动
  stop      停止
  restart   重启
  status    服务状态、监听端口、当前配置的客户端数量（不显示密钥）
  check     只做配置语法检查
  debug     停掉服务，前台运行 radiusd -X（调试完 Ctrl-C，再用 start 恢复）

环境变量: RADIUS_ETC（默认 ${RADIUS_ETC}）
EOF
}

radius_installed() { [ -d "$RADIUS_ETC" ] && have freeradius; }

radius_check() { # 语法检查：只看退出码，不输出密钥
    freeradius -XC -d "$RADIUS_ETC" >/dev/null 2>&1
}

radius_clients() {
    require_root
    radius_installed || die "FreeRADIUS 未安装，先运行: bash infra.sh radius"
    [ -f "$RADIUS_SRC" ] || die "缺少 ${RADIUS_SRC}"
    local dst="${RADIUS_ETC}/clients.conf" bak="" n
    if [ -f "$dst" ]; then
        bak="${dst}.bak.$(date +%Y%m%d%H%M%S)"
        cp -p "$dst" "$bak"
    fi
    install -m 640 -o root -g freerad "$RADIUS_SRC" "$dst" || die "写入 ${dst} 失败"
    if ! radius_check; then
        err "新的 clients.conf 没通过语法检查，已还原"
        if [ -n "$bak" ]; then
            cp -p "$bak" "$dst"
        else
            rm -f "$dst"
        fi
        die "检查具体错误: freeradius -XC -d ${RADIUS_ETC}"
    fi
    n="$(grep -cE '^[[:space:]]*client[[:space:]]' "$dst" 2>/dev/null || echo 0)"
    log "clients.conf 已替换，共 ${n} 个客户端（旧文件: ${bak:-无}）"
    systemctl restart "$RADIUS_UNIT" || die "重启失败: journalctl -u ${RADIUS_UNIT} -n 30"
    sleep 1
    radius_status_line
}

radius_status_line() {
    local act
    act="$(systemctl is-active "$RADIUS_UNIT" 2>/dev/null)"
    if [ "$act" = "active" ]; then
        log "freeradius 运行中（udp 1812/1813 由 radiusd 监听）"
    else
        err "freeradius 状态: ${act:-未知}，看日志: journalctl -u ${RADIUS_UNIT} -n 30"
        return 1
    fi
}

radius_status() {
    have systemctl || die "需要 systemd"
    echo "== freeradius =="
    systemctl is-active "$RADIUS_UNIT" 2>/dev/null | sed 's/^/  状态: /'
    systemctl is-enabled "$RADIUS_UNIT" 2>/dev/null | sed 's/^/  自启: /'
    echo "  监听:"
    ss -lunp 2>/dev/null | grep -E ':(1812|1813) ' | sed 's/^/    /' || echo "    (没有 1812/1813 监听)"
    if [ -f "${RADIUS_ETC}/clients.conf" ]; then
        echo "  客户端数量: $(grep -cE '^[[:space:]]*client[[:space:]]' "${RADIUS_ETC}/clients.conf")"
    fi
    radius_check && echo "  配置语法: OK" || echo "  配置语法: 有错误（bash radius.sh check）"
}

radius_debug() {
    require_root
    radius_installed || die "FreeRADIUS 未安装"
    warn "停掉 freeradius，前台运行 radiusd -X。Ctrl-C 后用 bash radius.sh start 恢复"
    systemctl stop "$RADIUS_UNIT" 2>/dev/null || true
    exec freeradius -X -d "$RADIUS_ETC"
}

radius_main() {
    local action="${1:-}"
    case "$action" in
        clients) radius_clients ;;
        start | stop | restart)
            require_root
            radius_installed || die "FreeRADIUS 未安装，先运行: bash infra.sh radius"
            systemctl "$action" "$RADIUS_UNIT" || die "${action} 失败: journalctl -u ${RADIUS_UNIT} -n 30"
            [ "$action" = stop ] || radius_status_line
            ;;
        status) radius_status ;;
        check) radius_check && log "配置语法 OK" || { err "配置有错误: freeradius -XC -d ${RADIUS_ETC}"; return 1; } ;;
        debug) radius_debug ;;
        '' | help | -h | --help) radius_usage ;;
        *)
            err "未知动作: ${action}"
            radius_usage
            return 2
            ;;
    esac
}

radius_main "$@"
