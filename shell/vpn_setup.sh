#!/usr/bin/env bash
# 兼容入口：旧参数转发到 vpn.sh。新用法请直接看 `bash vpn.sh help`。
#
# 旧参数        新命令
# soft          system init
# telegraf      system telegraf
# fail2ban      system fail2ban
# kernel        system bbr
# strongswan*   strongswan ...
# ca / caip     strongswan ca 59        caip6  strongswan ca 6
# iptables      system iptables-ipsec   net    system net
# check*        system speed / strongswan check / system trace
# all           strongswan all 59

if [ -z "${BASH_VERSION:-}" ]; then
    if command -v bash >/dev/null 2>&1; then
        exec bash "$0" "$@"
    fi
    echo "This script requires Bash. Run: bash $0 ..." >&2
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
        soft) bash "${DIR}/vpn.sh" system init ;;
        telegraf) bash "${DIR}/vpn.sh" system telegraf ;;
        fail2ban) bash "${DIR}/vpn.sh" system fail2ban ;;
        kernel) bash "${DIR}/vpn.sh" system bbr ;;
        strongswan) bash "${DIR}/vpn.sh" strongswan install 59 ;;
        strongswanconf) bash "${DIR}/vpn.sh" strongswan config 59 ;;
        strongswanconf_port) bash "${DIR}/vpn.sh" strongswan config-port 59 ;;
        strongswan59_all | strongswan5914_all) bash "${DIR}/vpn.sh" strongswan all 59 ;;
        strongswan_fix59) bash "${DIR}/vpn.sh" strongswan fix 59 ;;
        strongswan6) bash "${DIR}/vpn.sh" strongswan install 6 ;;
        strongswanconf6) bash "${DIR}/vpn.sh" strongswan config 6 ;;
        strongswanconf_port6) bash "${DIR}/vpn.sh" strongswan config-port 6 ;;
        strongswan6_all | strongswanall6) bash "${DIR}/vpn.sh" strongswan all 6 ;;
        strongswan_fix6) bash "${DIR}/vpn.sh" strongswan fix 6 ;;
        ca | caip) bash "${DIR}/vpn.sh" strongswan ca 59 ;;
        caip6) bash "${DIR}/vpn.sh" strongswan ca 6 ;;
        get_ip) bash "${DIR}/vpn.sh" system ip ;;
        iptables) bash "${DIR}/vpn.sh" system iptables-ipsec ;;
        net) bash "${DIR}/vpn.sh" system net ;;
        check) bash "${DIR}/vpn.sh" system speed ;;
        check_vpn) bash "${DIR}/vpn.sh" strongswan check 59 ;;
        check_vpn6) bash "${DIR}/vpn.sh" strongswan check 6 ;;
        check_mtr) bash "${DIR}/vpn.sh" system trace ;;
        all) bash "${DIR}/vpn.sh" strongswan all 59 ;;
        *)
            echo "未知参数: ${arg}。新用法: bash ${DIR}/vpn.sh help" >&2
            rc=2
            ;;
    esac || rc=$?
done
exit "$rc"
