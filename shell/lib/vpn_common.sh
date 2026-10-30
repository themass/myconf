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

xray_parse_x25519_keys() {
    local key_output="$1"
    local __private_var="${2:?}"
    local __public_var="${3:?}"

    # shellcheck disable=SC2034
    printf -v "$__private_var" '%s' "$(printf '%s\n' "$key_output" | awk -F': *' '
        $1 == "Private key" || $1 == "PrivateKey" { print $2; exit }
    ')"
    # shellcheck disable=SC2034
    printf -v "$__public_var" '%s' "$(printf '%s\n' "$key_output" | awk -F': *' '
        $1 == "Public key" || $1 == "Password" || $1 ~ /Public[Kk]ey/ { print $2; exit }
    ')"
}

xray_public_key_from_private() {
    local xray_bin="$1"
    local private_key="$2"

    "$xray_bin" x25519 -i "$private_key" 2>/dev/null | awk -F': *' '
        $1 == "Public key" || $1 == "Password" || $1 ~ /Public[Kk]ey/ { print $2; exit }
    '
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

xray_read_reality_link_fields() {
    local config_file="$1"

    python3 - "$config_file" <<'PY'
import json
import sys

path = sys.argv[1]
try:
    with open(path, encoding="utf-8") as f:
        config = json.load(f)
except (OSError, json.JSONDecodeError, UnicodeDecodeError):
    sys.exit(1)

for inbound in config.get("inbounds") or []:
    if inbound.get("protocol") != "vless":
        continue
    stream = inbound.get("streamSettings") or {}
    if stream.get("security") != "reality":
        continue
    reality = stream.get("realitySettings") or {}
    clients = (inbound.get("settings") or {}).get("clients") or []
    if not clients:
        continue
    client = clients[0]
    uuid = client.get("id")
    port = inbound.get("port")
    server_names = reality.get("serverNames") or []
    server_name = server_names[0] if server_names else ""
    private_key = reality.get("privateKey") or ""
    short_ids = reality.get("shortIds") or []
    short_id = short_ids[0] if short_ids else ""
    if not all([uuid, port, private_key, short_id, server_name]):
        continue
    print("\t".join([uuid, str(port), server_name, private_key, short_id]))
    sys.exit(0)

sys.exit(1)
PY
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

strongswan_resolve_charon_bin() {
    local candidate

    for candidate in \
        /usr/lib/ipsec/charon-systemd \
        /usr/sbin/charon-systemd \
        /usr/libexec/ipsec/charon-systemd; do
        if [ -x "$candidate" ]; then
            printf '%s\n' "$candidate"
            return 0
        fi
    done
    for candidate in /usr/lib/ipsec/charon /usr/libexec/ipsec/charon; do
        if [ -x "$candidate" ]; then
            printf '%s\n' "$candidate"
            return 0
        fi
    done
    return 1
}

strongswan_install_systemd_unit() {
    local charon_bin
    local unit_type="simple"
    local unit_path="/etc/systemd/system/strongswan.service"
    local install_cmd=(tee "$unit_path")

    if [ "$(id -u)" -ne 0 ]; then
        install_cmd=(sudo tee "$unit_path")
    fi

    # Do not reuse the upstream unit: its ExecStartPost runs swanctl before certs exist.
    charon_bin=$(strongswan_resolve_charon_bin) || {
        echo "charon or charon-systemd was not found after install" >&2
        return 1
    }
    case "$charon_bin" in
        *charon-systemd) unit_type="notify" ;;
    esac

    "${install_cmd[@]}" <<EOF
[Unit]
Description=strongSwan IPsec daemon
After=network-online.target
Wants=network-online.target

[Service]
Type=${unit_type}
ExecStart=${charon_bin}
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
EOF
    if [ -L /etc/systemd/system/strongswan-swanctl.service ]; then
        rm -f /etc/systemd/system/strongswan-swanctl.service
    fi
    systemctl daemon-reload 2>/dev/null || sudo systemctl daemon-reload
}

strongswan_reload_6() {
    if [ ! -f /etc/swanctl/x509ca/caCert.pem ]; then
        echo "缺少 CA 证书，请先运行: bash vpn_setup.sh caip6" >&2
        return 1
    fi
    if [ ! -f /etc/swanctl/x509/serverCert.pem ] || [ ! -f /etc/swanctl/private/serverCert.pem ]; then
        echo "缺少服务器证书或私钥，请先运行: bash vpn_setup.sh caip6" >&2
        return 1
    fi
    systemctl enable strongswan 2>/dev/null || sudo systemctl enable strongswan
    if ! systemctl restart strongswan 2>/dev/null; then
        sudo systemctl restart strongswan || return 1
    fi
    sleep 2
    if ! swanctl --load-all --noprompt 2>/dev/null; then
        sudo swanctl --load-all --noprompt || return 1
    fi
}
