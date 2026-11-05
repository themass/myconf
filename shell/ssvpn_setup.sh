#!/usr/bin/env bash
# 兼容入口：旧参数转发到 vpn.sh。新用法请直接看 `bash vpn.sh help`。
#
# 旧参数              新命令
# sspanel             ssr sspanel
# ssr                 ssr install
# xray / xray_all     xray install
# xray_regen          xray regen
# xray_check          xray check

if [ -z "${BASH_VERSION:-}" ]; then
    if command -v bash >/dev/null 2>&1; then
        exec bash "$0" "$@"
    fi
    echo "This script requires Bash. Run: bash $0 xray" >&2
    exit 2
fi

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ $# -eq 0 ]; then
    echo "本脚本只是兼容入口，请改用: bash ${DIR}/vpn.sh help"
    exit 0
fi

rc=0
for arg in "$@"; do
    case "$arg" in
        sspanel) bash "${DIR}/vpn.sh" ssr sspanel ;;
        ssr) bash "${DIR}/vpn.sh" ssr install ;;
        xray | xray_all) bash "${DIR}/vpn.sh" xray install ;;
        xray_regen) bash "${DIR}/vpn.sh" xray regen ;;
        xray_check) bash "${DIR}/vpn.sh" xray check ;;
        *)
            echo "未知参数: ${arg}。新用法: bash ${DIR}/vpn.sh help" >&2
            rc=2
            ;;
    esac || rc=$?
done
exit "$rc"
