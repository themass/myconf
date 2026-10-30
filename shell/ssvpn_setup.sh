#!/usr/bin/env bash

if [ -z "${BASH_VERSION:-}" ]; then
    if command -v bash >/dev/null 2>&1; then
        exec bash "$0" "$@"
    fi
    echo "This script requires Bash. Install bash or run: bash $0 xray" >&2
    exit 2
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib/vpn_common.sh
source "${SCRIPT_DIR}/lib/vpn_common.sh"
MYCONF_HOME="$(vpn_myconf_home)"

PANEL_WORKDIR=/home/web/webroot
PANEL_TMP_HOME=/home/web/soft
PANEL_SHELL_HOME=/home/web/work/myconf/shell

WORKDIR="${VPN_WORKDIR:-/root/work}"
TMP_HOME="${VPN_TMP_HOME:-/root/soft}"
SHELL_HOME="${SCRIPT_DIR}"
#https://doub.io/ss-jc13/
setup_sspanel() 
{
	cd ${PANEL_WORKDIR}
	rm -rf ss-panel
	git clone https://github.com/orvice/ss-panel.git -b master
	cd ss-panel
	curl -sS https://getcomposer.org/installer | php
	php composer.phar  install
	cp ${PANEL_SHELL_HOME}/../ss_panel/env  .env
	php xcat migrate
	chmod -R 777 storage
	
	#cp ${PANEL_SHELL_HOME}/../php/config.php ${PANEL_WORKDIR}/ss-panel/lib
	#mysql -u vpn@server -p -hmysql.sspacee.com vpn < ${PANEL_WORKDIR}/ss-panel/invite_code.sql
	#mysql -u vpn@server -p -hmysql.sspacee.com vpn < ${PANEL_WORKDIR}/ss-panel/ss_node.sql
	#mysql -u vpn@server -p -hmysql.sspacee.com vpn < ${PANEL_WORKDIR}/ss-panel/ss_reset_pwd.sql
	#mysql -u vpn@server -p -hmysql.sspacee.com vpn < ${PANEL_WORKDIR}/ss-panel/ss_user_admin.sql
	#mysql -u vpn@server -p -hmysql.sspacee.com vpn < ${PANEL_WORKDIR}/ss-panel/user.sql
	#echo 'http://hostggg.com/pwd.php?pwd=1993'
}
setup_ssr() 
{
	cd ${WORKDIR}
	#	git clone -b manyuser https://github.com/ToyoDAdoubi/shadowsocksr.git
	
	git clone  https://github.com/themass/shadowsocksr.git
	cd shadowsocksr
	bash setup_cymysql.sh
	bash initcfg.sh
	cp ${SHELL_HOME}/../ssr_conf/* .
}

# Install Xray-core and create a VLESS + REALITY server configuration.
#
# Optional environment variables:
#   XRAY_SERVER_ADDRESS  Override the client link address (auto-detected if unset)
#   XRAY_PORT            Listening port (default: 443)
#   XRAY_DEST            REALITY fallback, including port
#   XRAY_SERVER_NAME     REALITY SNI/serverName
#   XRAY_CONFIG_DIR      Config directory (default: /usr/local/etc/xray)
#   XRAY_CONFIG_FORCE    Set to 1 to replace an existing config after backup
setup_xray()
{
    if [ "$(id -u)" -ne 0 ]; then
        echo "setup_xray must be run as root" >&2
        return 1
    fi

    local installer_url="https://github.com/XTLS/Xray-install/raw/main/install-release.sh"
    local installer_file
    local xray_bin
    local config_dir="${XRAY_CONFIG_DIR:-/usr/local/etc/xray}"
    local config_file="${config_dir}/config.json"
    local config_created=0
    local backup_file
    local key_output
    local private_key
    local public_key
    local uuid
    local short_id
    local server_address
    local link
    local config_values
    local port="${XRAY_PORT:-443}"
    local dest="${XRAY_DEST:-www.samsung.com:443}"
    local server_name="${XRAY_SERVER_NAME:-www.samsung.com}"

    local config_parse_ok=0

    installer_file=$(mktemp "${TMPDIR:-/tmp}/xray-install.XXXXXX.sh") || {
        echo "Unable to create a temporary file" >&2
        return 1
    }

    # Prefer curl, then wget. Do not silently modify the host package set.
    if command -v curl >/dev/null 2>&1; then
        if ! curl -fsSL --retry 3 --retry-delay 2 "$installer_url" -o "$installer_file"; then
            rm -f "$installer_file"
            echo "Failed to download the official Xray installer" >&2
            return 1
        fi
    elif command -v wget >/dev/null 2>&1; then
        if ! wget -q --tries=3 -O "$installer_file" "$installer_url"; then
            rm -f "$installer_file"
            echo "Failed to download the official Xray installer" >&2
            return 1
        fi
    else
        rm -f "$installer_file"
        echo "Neither curl nor wget is installed; install one first" >&2
        return 1
    fi

    # JSON_PATH keeps the systemd unit aligned when a non-default config
    # directory is requested.
    # The official script is normally invoked with `bash -c ... @ install`;
    # when it is saved to a file, `@` would become a real argument and the
    # installer may reject it as an unknown option.
    if ! JSON_PATH="$config_dir" bash "$installer_file" install; then
        rm -f "$installer_file"
        echo "Xray installation failed" >&2
        return 1
    fi
    rm -f "$installer_file"

    xray_bin=$(command -v xray 2>/dev/null || true)
    if [ -z "$xray_bin" ] && [ -x /usr/local/bin/xray ]; then
        xray_bin=/usr/local/bin/xray
    fi
    if [ -z "$xray_bin" ]; then
        echo "Xray installation completed, but xray is not in PATH" >&2
        return 1
    fi

    mkdir -p "$config_dir" || return 1

    if [ -f "$config_file" ] && [ "${XRAY_CONFIG_FORCE:-0}" != "1" ]; then
        echo "Existing Xray config preserved: $config_file"
        echo "Set XRAY_CONFIG_FORCE=1 to back it up and generate a new config."
    else
        if [ -f "$config_file" ]; then
            backup_file="${config_file}.bak.$(date +%Y%m%d%H%M%S)"
            cp -p "$config_file" "$backup_file" || return 1
            echo "Existing config backed up to $backup_file"
        fi

        uuid=$($xray_bin uuid) || {
            echo "Unable to generate Xray UUID" >&2
            return 1
        }
        key_output=$($xray_bin x25519) || {
            echo "Unable to generate X25519 key pair" >&2
            return 1
        }

        xray_parse_x25519_keys "$key_output" private_key public_key
        short_id=$(openssl rand -hex 8 2>/dev/null) || {
            echo "openssl is required to generate the REALITY short ID" >&2
            return 1
        }

        if [ -z "$private_key" ] || [ -z "$public_key" ]; then
            echo "Unable to parse xray x25519 output:" >&2
            printf '%s\n' "$key_output" >&2
            return 1
        fi

        cat > "$config_file" <<EOF
{
  "log": {
    "loglevel": "warning"
  },
  "inbounds": [
    {
      "port": ${port},
      "listen": "0.0.0.0",
      "protocol": "vless",
      "settings": {
        "clients": [
          {
            "id": "${uuid}",
            "flow": "xtls-rprx-vision"
          }
        ],
        "decryption": "none"
      },
      "streamSettings": {
        "network": "tcp",
        "security": "reality",
        "realitySettings": {
          "show": false,
          "dest": "${dest}",
          "xver": 0,
          "serverNames": [
            "${server_name}"
          ],
          "privateKey": "${private_key}",
          "shortIds": [
            "${short_id}"
          ]
        }
      },
      "sniffing": {
        "enabled": true,
        "destOverride": [
          "http",
          "tls"
        ]
      }
    }
  ],
  "outbounds": [
    {
      "protocol": "freedom",
      "settings": {}
    }
  ]
}
EOF
        # Recent official installers run the service as the dedicated xray
        # user.  Make the generated config readable by that user while keeping
        # it inaccessible to other users; retain a root-only fallback for old
        # installations that do not have an xray group yet.
        if getent group xray >/dev/null 2>&1 && id xray >/dev/null 2>&1; then
            chown root:xray "$config_dir" "$config_file" || return 1
            chmod 750 "$config_dir" || return 1
            chmod 640 "$config_file" || return 1
        else
            chmod 700 "$config_dir" || return 1
            chmod 600 "$config_file" || return 1
        fi
        config_created=1
    fi

    if ! xray_validate_config "$xray_bin" "$config_file"; then
        echo "Xray configuration test failed: $config_file" >&2
        return 1
    fi

    if command -v systemctl >/dev/null 2>&1 && systemctl cat xray.service >/dev/null 2>&1; then
        systemctl enable xray.service >/dev/null 2>&1 || true
        systemctl restart xray.service || {
            echo "Xray config is valid, but the service failed to restart" >&2
            return 1
        }
    else
        echo "systemd/xray.service was not found; start Xray manually after configuring it."
    fi

    server_address=$(detect_server_address 2>/dev/null || true)
    if [ -n "$server_address" ] && [ -z "${XRAY_SERVER_ADDRESS:-}" ]; then
        echo "Detected server address: $server_address"
    fi

    # When re-running against an existing config, recover link fields if possible.
    if [ "$config_created" -eq 0 ]; then
        if config_values=$(xray_read_reality_link_fields "$config_file" 2>/dev/null); then
            IFS=$'\t' read -r uuid port server_name private_key short_id <<EOF
$config_values
EOF
            public_key=$(xray_public_key_from_private "$xray_bin" "$private_key")
            config_parse_ok=1
        else
            echo "Existing config is not a readable VLESS+REALITY profile." >&2
            echo "Set XRAY_CONFIG_FORCE=1 to back it up and generate a new config." >&2
        fi
    else
        config_parse_ok=1
    fi

    echo "Xray installed and configuration validated: $config_file"
    if [ -n "$server_address" ] && [ -n "$uuid" ] && [ -n "$public_key" ] && [ -n "$short_id" ]; then
        link="vless://${uuid}@${server_address}:${port}?flow=xtls-rprx-vision&encryption=none&type=tcp&security=reality&sni=${server_name}&fp=chrome&pbk=${public_key}&sid=${short_id}#Xray-REALITY"
        echo "VLESS REALITY link:"
        echo "$link"
    elif [ -z "$server_address" ]; then
        echo "Unable to detect server address; set XRAY_SERVER_ADDRESS to print a complete VLESS link."
    elif [ "$config_parse_ok" -eq 0 ]; then
        echo "Run with XRAY_CONFIG_FORCE=1 to regenerate config and print a new VLESS link."
    else
        echo "Could not derive REALITY public key from config; check: $xray_bin x25519 -i <privateKey>"
    fi
}

## -----------------------
## Show help message
## -----------------------
usage() 
{
    echo "Available arguments as below:"
    echo "sspanel           Setup setup_sspanel"
    echo "ssr          Setup setup_ssr"
    echo "xray         Install or upgrade Xray-core (VLESS + REALITY)"
    echo "xray_all     Same as xray (one-shot install + config + link)"
}

## =====================================
## The main process
## =====================================
if [ $# != 0 ]; then
    for arg in $*; do
        case "$arg" in
            sspanel)            setup_sspanel;;
            ssr)          setup_ssr;;
            xray|xray_all)         setup_xray;;
        esac
    done
else
    usage
fi
