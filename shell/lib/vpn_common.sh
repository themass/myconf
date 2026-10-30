#!/usr/bin/env bash
# Shared helpers for vpn_setup.sh and ssvpn_setup.sh

vpn_myconf_home() {
    if [ -n "${MYCONF_HOME:-}" ]; then
        printf '%s\n' "$MYCONF_HOME"
        return
    fi
    if [ -n "${BASH_SOURCE[1]:-}" ]; then
        MYCONF_HOME="$(cd "$(dirname "${BASH_SOURCE[1]}")/.." && pwd)"
    else
        MYCONF_HOME="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
    fi
    printf '%s\n' "$MYCONF_HOME"
}

is_public_ipv4() {
    local ip="${1:-}"

    [[ "$ip" =~ ^([0-9]{1,3}\.){3}[0-9]{1,3}$ ]] || return 1
    case "$ip" in
        10.*|127.*|0.*|255.*|192.168.*|172.1[6-9].*|172.2[0-9].*|172.3[0-1].*)
            return 1
            ;;
    esac
    return 0
}

detect_server_address() {
    local ip=""
    local url

    if [ -n "${XRAY_SERVER_ADDRESS:-}" ]; then
        printf '%s\n' "$XRAY_SERVER_ADDRESS"
        return 0
    fi

    if command -v curl >/dev/null 2>&1; then
        for url in \
            "http://100.100.100.200/latest/meta-data/eipv4" \
            "http://100.100.100.200/latest/meta-data/public-ipv4" \
            "https://api.ipify.org" \
            "https://ifconfig.me/ip" \
            "https://icanhazip.com"; do
            ip=$(curl -4fsS --connect-timeout 2 --max-time 5 "$url" 2>/dev/null | tr -d '[:space:]')
            if is_public_ipv4 "$ip"; then
                printf '%s\n' "$ip"
                return 0
            fi
        done
    fi

    if command -v ip >/dev/null 2>&1; then
        ip=$(ip -4 route get 1.1.1.1 2>/dev/null | awk '{for (i = 1; i <= NF; i++) if ($i == "src") { print $(i + 1); exit }}')
        if is_public_ipv4 "$ip"; then
            printf '%s\n' "$ip"
            return 0
        fi
    fi

    ip=$(hostname -I 2>/dev/null | awk '{print $1}')
    ip=${ip// /}
    if is_public_ipv4 "$ip"; then
        printf '%s\n' "$ip"
        return 0
    fi

    return 1
}

get_ip() {
    local IP=""

    IP=$(detect_server_address 2>/dev/null || true)
    if [ -n "$IP" ]; then
        echo "$IP"
        return
    fi

    IP=$(ip addr 2>/dev/null | egrep -o '[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}' | egrep -v "^192\.168|^172\.1[6-9]\.|^172\.2[0-9]\.|^172\.3[0-2]\.|^10\.|^127\.|^255\.|^0\." | head -n 1)
    [ -z "$IP" ] && IP=$(wget -qO- -t1 -T2 ipv4.icanhazip.com 2>/dev/null || true)
    [ -z "$IP" ] && IP=$(wget -qO- -t1 -T2 ipinfo.io/ip 2>/dev/null || true)
    echo "$IP"
}

get_netdev() {
    local dev=""

    if command -v ip >/dev/null 2>&1; then
        dev=$(ip -4 route show default 2>/dev/null | awk '{for (i = 1; i <= NF; i++) if ($i == "dev") { print $(i + 1); exit }}')
        if [ -n "$dev" ]; then
            echo "$dev"
            return
        fi
    fi
    echo eth0
}

apply_server_ip_template() {
    local target_file="$1"
    local server_ip="$2"

    [ -f "$target_file" ] || return 0
    if [ "$(id -u)" -eq 0 ]; then
        sed -i "s/{{SERVER_IP}}/${server_ip}/g" "$target_file"
    else
        sudo sed -i "s/{{SERVER_IP}}/${server_ip}/g" "$target_file"
    fi
}

install_config_template() {
    local template="$1"
    local target="$2"
    local server_ip="${3:-}"
    local backup=""
    local install_cmd=(cp)

    if [ "$(id -u)" -ne 0 ]; then
        install_cmd=(sudo cp)
    fi

    if [ ! -f "$template" ]; then
        echo "Missing config template: $template" >&2
        return 1
    fi
    if [ -f "$target" ]; then
        backup="${target}.bak.$(date +%Y%m%d%H%M%S)"
        if [ "$(id -u)" -eq 0 ]; then
            cp -p "$target" "$backup"
        else
            sudo cp -p "$target" "$backup"
        fi
    fi
    "${install_cmd[@]}" "$template" "$target"
    if [ -n "$server_ip" ]; then
        apply_server_ip_template "$target" "$server_ip"
    fi
}

xray_validate_config() {
    local xray_bin="$1"
    local config_file="$2"

    if "$xray_bin" run -test -config "$config_file" >/dev/null 2>&1; then
        return 0
    fi
    if "$xray_bin" test -c "$config_file" >/dev/null 2>&1; then
        return 0
    fi
    return 1
}

openssl_version_major() {
    if ! command -v openssl >/dev/null 2>&1; then
        echo 0
        return
    fi
    openssl version 2>/dev/null | sed -n 's/.*OpenSSL \([0-9]*\).*/\1/p'
}

strongswan_pick_legacy_version() {
    local openssl_major
    openssl_major=$(openssl_version_major)
    if [ "${openssl_major:-0}" -ge 3 ]; then
        echo 5.9.14
        return
    fi
    echo 5.6.3
}

strongswan_start_service() {
    systemctl daemon-reload 2>/dev/null || true
    if systemctl list-unit-files 2>/dev/null | grep -q '^strongswan\.service'; then
        systemctl enable strongswan
        systemctl restart strongswan
        return
    fi
    if systemctl list-unit-files 2>/dev/null | grep -q '^strongswan-starter\.service'; then
        systemctl enable strongswan-starter
        systemctl restart strongswan-starter
        return
    fi
    if systemctl list-unit-files 2>/dev/null | grep -q '^ipsec\.service'; then
        systemctl enable ipsec
        systemctl restart ipsec
        return
    fi
    if command -v ipsec >/dev/null 2>&1; then
        ipsec restart
        return
    fi
    echo "strongSwan installed, but no service unit was found." >&2
}
