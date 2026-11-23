#!/usr/bin/env bash
# LiveKit Server 自托管（104 应用机）：二进制安装 + systemd(web 用户) + 配置渲染 + 冒烟。
#
#   bash livekit.sh install     下载二进制、渲染配置、装 systemd unit 并启动
#   bash livekit.sh status      服务状态 + 本机信令自证
#   bash livekit.sh rotate-key  换 API key/secret（重启服务；服务端/worker 的 env 要同步改）
#   bash livekit.sh help
#
# 设计约束（2026-11-23 方案 B 拍板）：
#   * 不用 docker（104 没装），直接用上游 release 二进制，装在 /home/web/opt/livekit，
#     配置 /home/web/etc/livekit/config.yaml（600），以 web 用户跑 systemd unit。
#   * 信令绑 127.0.0.1:7880，外部流量走 https://livekit.ok123find.top（nginx 在 8.217.122.83 终结 TLS 后跨机转发）。
#   * 媒体 UDP 直接对外：node_ip 钉死本机公网 IP（见 LIVEKIT_NODE_IP）。
#
# 环境变量：
#   LIVEKIT_VERSION      上游 release tag（默认 v1.13.11）
#   LIVEKIT_NODE_IP      媒体 advertise 的公网 IP（默认 104.160.191.87；换机器要改）
#   LIVEKIT_PORT_RANGE   媒体 UDP 段，格式 start-end（默认 50000-50019）
#   LIVEKIT_API_KEY / LIVEKIT_API_SECRET
#                        已存在 config.yaml 里则自动沿用；首次装自动生成（rotate-key 强制换新）。
#                        这两个值之后要配进 companion 服务端和 voice worker 的 .env。

if [ -z "${BASH_VERSION:-}" ]; then
    command -v bash >/dev/null 2>&1 && exec bash "$0" "$@"
    echo "需要 bash: bash $0 ..." >&2
    exit 2
fi

VPN_SHELL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export VPN_SHELL_DIR
# shellcheck source=lib/common.sh
source "${VPN_SHELL_DIR}/lib/common.sh"

LIVEKIT_VERSION="${LIVEKIT_VERSION:-v1.13.11}"
LIVEKIT_NODE_IP="${LIVEKIT_NODE_IP:-104.160.191.87}"
LIVEKIT_PORT_RANGE="${LIVEKIT_PORT_RANGE:-50000-50019}"

LIVEKIT_PREFIX="/home/web/opt/livekit"
LIVEKIT_ETC="/home/web/etc/livekit"
LIVEKIT_CONF="${LIVEKIT_ETC}/config.yaml"
LIVEKIT_UNIT="/etc/systemd/system/livekit.service"

livekit_usage() {
    sed -n '2,20p' "$0" | sed 's/^# \{0,1\}//'
}

# 从已有 config.yaml 里抠出 key/secret（重装不丢已下发的 token 签名密钥）。
livekit_existing_keys() {
    [ -f "$LIVEKIT_CONF" ] || return 0
    local line key secret
    line="$(grep -m1 -E '^  [A-Za-z0-9_]+: .+$' "$LIVEKIT_CONF" | head -1)" || return 0
    key="$(printf '%s' "$line" | sed -E 's/^  ([^:]+):.*/\1/' | tr -d ' ')"
    secret="$(printf '%s' "$line" | sed -E 's/^[^:]+: //' | tr -d ' ')"
    [ -n "$key" ] && [ -n "$secret" ] || return 0
    LIVEKIT_API_KEY="$key"
    LIVEKIT_API_SECRET="$secret"
}

livekit_install() {
    require_root
    ensure_cmds curl tar

    local arch start end
    arch="$(detect_arch)"
    [ "$arch" = "amd64" ] || die "上游只有 amd64/arm64 包，本机架构=$arch，先确认 release 资产名"
    start="${LIVEKIT_PORT_RANGE%-*}"
    end="${LIVEKIT_PORT_RANGE#*-}"
    [ -n "$start" ] && [ -n "$end" ] || die "LIVEKIT_PORT_RANGE 格式要 start-end，收到: $LIVEKIT_PORT_RANGE"

    # 端口冲突检查：信令 7880（允许本服务自己占）、TURN 7881 tcp+udp、7882 udp、媒体段抽查
    assert_port_free tcp 7880 livekit-server LIVEKIT_PORT
    assert_port_free tcp 7881 livekit-server LIVEKIT_TURN_TCP_PORT
    assert_port_free udp 7881 livekit-server LIVEKIT_TURN_UDP_PORT
    assert_port_free udp 7882 livekit-server LIVEKIT_RTC_UDP_PORT
    assert_port_free udp "$start" livekit-server LIVEKIT_PORT_RANGE

    if [ ! -f "$LIVEKIT_CONF" ]; then
        livekit_existing_keys || true
        if [ -z "${LIVEKIT_API_KEY:-}" ]; then
            LIVEKIT_API_KEY="lk_$(rand_hex 4)"
            LIVEKIT_API_SECRET="$(rand_hex 24)"
            log "生成新 API 键对: key=$LIVEKIT_API_KEY（secret 已写入 $LIVEKIT_CONF，600）"
        fi
        install_template "${VPN_SHELL_DIR}/../conf/livekit/config.yaml" "$LIVEKIT_CONF" 600 \
            LIVEKIT_API_KEY="$LIVEKIT_API_KEY" LIVEKIT_API_SECRET="$LIVEKIT_API_SECRET" \
            LIVEKIT_NODE_IP="$LIVEKIT_NODE_IP"
        # 端口段用环境变量微调时改渲染结果里的两行（模板默认 50000-50019）.
        sed -i -E "s/^  port_range_start: .*/  port_range_start: ${start}/; s/^  port_range_end: .*/  port_range_end: ${end}/" "$LIVEKIT_CONF"
    else
        log "已有 $LIVEKIT_CONF，保持不动（改配置请手工编辑后 livekit.sh restart）"
        livekit_existing_keys || true
    fi
    chown web:web "$LIVEKIT_CONF"

    # 二进制：带版本目录，符号链接可回滚。
    local dir="${LIVEKIT_PREFIX}/${LIVEKIT_VERSION}" tarball url
    if [ -x "${dir}/livekit-server" ]; then
        log "二进制已存在: ${dir}/livekit-server"
    else
        url="https://github.com/livekit/livekit-server/releases/download/${LIVEKIT_VERSION}/livekit_${LIVEKIT_VERSION#v}_linux_${arch}.tar.gz"
        tarball="$(mktemp /tmp/livekit.XXXXXX.tar.gz)"
        log "下载 $url"
        curl -fL --retry 3 -o "$tarball" "$url" || die "下载失败：确认机器能访问 github.com（104 已验证可达）"
        mkdir -p "$dir"
        tar -xzf "$tarball" -C "$dir" livekit-server || die "解包失败（资产内路径变了？tar -tzf 看一下）"
        rm -f "$tarball"
        ln -sfn "$dir" "${LIVEKIT_PREFIX}/current"
    fi
    ln -sfn "$dir" "${LIVEKIT_PREFIX}/current" 2>/dev/null || true
    mkdir -p "$LIVEKIT_PREFIX"
    chown -R web:web "$LIVEKIT_PREFIX"
    # current 软链要在 unit 里可解析；unit 里写死的 /home/web/opt/livekit/livekit-server 用一层脚本兜底。
    cat >"${LIVEKIT_PREFIX}/livekit-server" <<EOF
#!/bin/sh
exec ${LIVEKIT_PREFIX}/current/livekit-server "\$@"
EOF
    chmod 755 "${LIVEKIT_PREFIX}/livekit-server"
    chown web:web "${LIVEKIT_PREFIX}/livekit-server"

    install_file "${VPN_SHELL_DIR}/../conf/livekit/livekit.service" "$LIVEKIT_UNIT" 644
    systemctl daemon-reload
    systemctl enable livekit >/dev/null 2>&1

    open_port tcp 7881
    open_port udp 7881
    open_port udp 7882
    open_port udp "$start" >/dev/null 2>&1 || true
    # 媒体段逐个 open_port 太啰嗦，直接给 ufw 加段（有 ufw 才加）。
    if have ufw && ufw status 2>/dev/null | grep -q "Status: active"; then
        ufw allow "${start}:${end}/udp" >/dev/null && log "ufw 已放行 ${start}:${end}/udp"
    fi

    svc_enable_restart livekit || die "livekit.service 启动失败: journalctl -u livekit -n 50"
    sleep 1
    livekit_status
    cat <<EOF

下一步（都不在本脚本范围，按 README-livekit.md 执行）：
  1. 云控制台安全组放行：udp ${start}-${end}, tcp 7881, udp 7881, udp 7882（104）。
  2. companion 服务端 / voice worker .env：
       LIVEKIT_URL=wss://livekit.ok123find.top
       LIVEKIT_API_KEY=${LIVEKIT_API_KEY:-<见 $LIVEKIT_CONF>}
       LIVEKIT_API_SECRET=<见 $LIVEKIT_CONF>
  3. 8.217 上装 conf/nginx/app-83/livekit-ok123find.conf + certbot 签证书 + reload。
EOF
    remind_security_group
}

livekit_status() {
    systemctl is-active livekit >/dev/null 2>&1 \
        && log "livekit.service: active" \
        || { warn "livekit.service 未运行"; systemctl status livekit --no-pager -n 20 || true; return 1; }
    local code
    code="$(curl -s -o /dev/null -w '%{http_code}' --max-time 5 http://127.0.0.1:7880/ 2>/dev/null)"
    [ "$code" = "200" ] && log "本机信令 http://127.0.0.1:7880 → 200 OK" \
        || warn "本机信令探测异常: http=$code（LiveKit 根路径应回 200）"
    ss -lunp 2>/dev/null | grep -E ':(7882|7881) ' | head -4
}

livekit_rotate_key() {
    require_root
    [ -f "$LIVEKIT_CONF" ] || die "先 install"
    LIVEKIT_API_KEY="lk_$(rand_hex 4)"
    LIVEKIT_API_SECRET="$(rand_hex 24)"
    # 只替换 keys: 块下第一行（rtc/logging 的子键也是两格缩进，sed 全局替换会误伤）。
    awk -v k="$LIVEKIT_API_KEY" -v s="$LIVEKIT_API_SECRET" '
        !done && $1 ~ /^[A-Za-z0-9_]+:$/ && inkeys { $0 = "  " k ": " s; done=1 }
        /^keys:/ { inkeys=1 }
        { print }' "$LIVEKIT_CONF" >"${LIVEKIT_CONF}.new" || die "awk 失败"
    mv "${LIVEKIT_CONF}.new" "$LIVEKIT_CONF"
    chown web:web "$LIVEKIT_CONF"
    log "已换新键对 key=$LIVEKIT_API_KEY；服务端/worker .env 同步后重启它们"
    svc_enable_restart livekit
}

case "${1:-help}" in
    install) livekit_install ;;
    status) livekit_status ;;
    rotate-key) livekit_rotate_key ;;
    restart) require_root; svc_enable_restart livekit; livekit_status ;;
    help|"") livekit_usage ;;
    *) die "未知动作: $1（help）" ;;
esac
