#!/usr/bin/env bash
# companion 服务端 / voice worker 切到自托管 LiveKit（以及切回 LiveKit Cloud）。只在 104 上跑。
#
#   bash livekit-companion.sh status     当前 LIVEKIT_URL + 两个进程状态（不打印密钥）
#   bash livekit-companion.sh switch     .env 的 LIVEKIT_* 三项指向自托管，然后重启 api+voice
#   bash livekit-companion.sh rollback   还原最近一次 switch 前的 .env 备份，重启
#   bash livekit-companion.sh help
#
# 设计约束（2026-11-23 方案 B）：
#   * 一个 LIVEKIT_URL 三处消费（worker 连入、服务端建房、下发给 App），必须用公网域名一个值：
#     wss://livekit.ok123find.top。worker 与 LiveKit 同机也走域名（TLS 经 nginx 两跳绕一圈，量很小），
#     这样三处不会分叉。
#   * API 键对从 /home/web/etc/livekit/config.yaml 读，脚本只打印 key（非密钥），secret 全程不打印
#     （也不出现在命令行里，避免进 ps）。
#   * switch 前把 .env 备份成 .env.bak-<时间戳>-livekit，rollback 就是取回最近那个备份。
#   * 两个进程由 companion-agent/scripts/process.sh 管（setsid + PID 文件），切完必须重启它们。

if [ -z "${BASH_VERSION:-}" ]; then
    command -v bash >/dev/null 2>&1 && exec bash "$0" "$@"
    echo "需要 bash: bash $0 ..." >&2
    exit 2
fi

VPN_SHELL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export VPN_SHELL_DIR
# shellcheck source=lib/common.sh
source "${VPN_SHELL_DIR}/lib/common.sh"

LIVEKIT_URL_DEFAULT="${LIVEKIT_URL_DEFAULT:-wss://livekit.ok123find.top}"
LIVEKIT_URL_VALUE="${LIVEKIT_URL:-$LIVEKIT_URL_DEFAULT}"
LIVEKIT_CONF="${LIVEKIT_CONF:-/home/web/etc/livekit/config.yaml}"
CA_DIR="${CA_DIR:-/home/web/webroot/companion-agent}"
ENV_FILE="${CA_DIR}/server/.env"
PROCESS_SH="${CA_DIR}/scripts/process.sh"

livekit_companion_usage() {
    sed -n '2,18p' "$0" | sed 's/^# \{0,1\}//'
}

# 从 livekit config.yaml 的 keys: 块取第一行（awk 输出到环境变量，不落盘不打印）。
livekit_companion_read_keys() {
    local line
    line="$(awk '/^keys:[[:space:]]*$/{f=1; next} f && NF && $0 ~ /^[[:space:]]+[A-Za-z0-9_]+:[[:space:]]*\S/ { sub(/^[[:space:]]+/,""); print; exit }' "$LIVEKIT_CONF")"
    [ -n "$line" ] || die "$LIVEKIT_CONF 里没找到 keys 块——先 bash livekit.sh install"
    LIVEKIT_API_KEY="${line%%:*}"
    LIVEKIT_API_SECRET="${line#*: }"
    LIVEKIT_API_SECRET="${LIVEKIT_API_SECRET//[[:space:]]/}"
    [ -n "$LIVEKIT_API_KEY" ] && [ -n "$LIVEKIT_API_SECRET" ] || die "解析 keys 失败（$LIVEKIT_CONF）"
}

livekit_companion_show_url() {
    grep -E '^LIVEKIT_URL=' "$ENV_FILE" | sed 's/^/  /' || warn "  .env 里没有 LIVEKIT_URL"
    printf '  LIVEKIT_API_KEY 行数=%s  LIVEKIT_API_SECRET 行数=%s（值不打印）\n' \
        "$(grep -c '^LIVEKIT_API_KEY=' "$ENV_FILE")" "$(grep -c '^LIVEKIT_API_SECRET=' "$ENV_FILE")"
}

livekit_companion_status() {
    [ -f "$ENV_FILE" ] || die "找不到 $ENV_FILE（本脚本只在 104 上跑）"
    log "$ENV_FILE 现状:"
    livekit_companion_show_url
    local code
    code="$(curl -s -o /dev/null -w '%{http_code}' --max-time 8 "$LIVEKIT_URL_VALUE/" 2>/dev/null)"
    [ "$code" = "200" ] && log "$LIVEKIT_URL_VALUE → 200（nginx 两跳通）" \
        || warn "$LIVEKIT_URL_VALUE 探测异常: http=$code"
    su -s /bin/bash web -c "cd '$CA_DIR' && bash '$PROCESS_SH' status" 2>&1 | sed 's/^/  /'
}

livekit_companion_switch() {
    require_root
    [ -f "$ENV_FILE" ] || die "找不到 $ENV_FILE（本脚本只在 104 上跑）"
    [ -f "$LIVEKIT_CONF" ] || die "找不到 $LIVEKIT_CONF——先 bash livekit.sh install"
    [ -x "$PROCESS_SH" ] || die "找不到 $PROCESS_SH"

    livekit_companion_read_keys
    local bak="${ENV_FILE}.bak-$(date +%Y%m%d-%H%M%S)-livekit"
    cp -a "$ENV_FILE" "$bak"
    log "已备份: $bak（rollback 会取回它）"

    # 密钥经环境变量喂给 awk：命令行里没有明文，ps 看不到。
    LK_URL="$LIVEKIT_URL_VALUE" LK_KEY="$LIVEKIT_API_KEY" LK_SECRET="$LIVEKIT_API_SECRET" \
    awk '
        BEGIN { url=ENVIRON["LK_URL"]; key=ENVIRON["LK_KEY"]; sec=ENVIRON["LK_SECRET"]
                u=k=s=0 }
        /^LIVEKIT_URL=/        { print "LIVEKIT_URL=\"" url "\"";       u=1; next }
        /^LIVEKIT_API_KEY=/    { print "LIVEKIT_API_KEY=\"" key "\"";   k=1; next }
        /^LIVEKIT_API_SECRET=/ { print "LIVEKIT_API_SECRET=\"" sec "\""; s=1; next }
        { print }
        END { if (!u) print "LIVEKIT_URL=\"" url "\""
              if (!k) print "LIVEKIT_API_KEY=\"" key "\""
              if (!s) print "LIVEKIT_API_SECRET=\"" sec "\"" }
    ' "$ENV_FILE" >"${ENV_FILE}.new" || die "awk 改写失败"
    chmod --reference="$ENV_FILE" "${ENV_FILE}.new" 2>/dev/null || chmod 600 "${ENV_FILE}.new"
    chown --reference="$ENV_FILE" "${ENV_FILE}.new" 2>/dev/null || chown web:web "${ENV_FILE}.new"
    mv "${ENV_FILE}.new" "$ENV_FILE"
    log ".env 已指向自托管（key=$LIVEKIT_API_KEY）:"
    livekit_companion_show_url

    log "重启 api + voice…"
    su -s /bin/bash web -c "cd '$CA_DIR' && bash '$PROCESS_SH' restart all" 2>&1 | sed 's/^/  /' \
        || die "重启失败：bash $PROCESS_SH logs voice 50"
    log "完成。验收看 companion 服务端/voice 日志与手机通话（README-livekit.md §5）。"
}

livekit_companion_rollback() {
    require_root
    local bak
    bak="$(ls -1t "${ENV_FILE}.bak-"*-livekit 2>/dev/null | head -1)"
    [ -n "$bak" ] || die "没有 .env.bak-*-livekit 备份，不猜旧值——请手工填回 LiveKit Cloud 的三个值"
    log "还原: $bak"
    cp -a "$bak" "$ENV_FILE"
    livekit_companion_show_url
    su -s /bin/bash web -c "cd '$CA_DIR' && bash '$PROCESS_SH' restart all" 2>&1 | sed 's/^/  /' \
        || die "重启失败：bash $PROCESS_SH logs voice 50"
}

case "${1:-help}" in
    status)   livekit_companion_status ;;
    switch)   livekit_companion_switch ;;
    rollback) livekit_companion_rollback ;;
    help|"")  livekit_companion_usage ;;
    *) die "未知动作: $1（help）" ;;
esac
