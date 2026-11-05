#!/usr/bin/env bash
# Xray-core 服务端：VLESS + Reality（TCP，默认 443）。
#
# 用法（通过 vpn.sh 调用）：
#   vpn.sh xray install     安装 Xray，生成配置，启动，输出客户端链接
#   vpn.sh xray upgrade     升级二进制到 XRAY_VERSION（配置不动）
#   vpn.sh xray regen       备份旧配置，重新生成 UUID 和 Reality 密钥
#   vpn.sh xray links       输出客户端链接
#   vpn.sh xray check       配置、服务、端口、Reality 自检
#   vpn.sh xray status | restart
#
# 安装方式：下载固定版本的官方发布包，用 .dgst 里的 SHA256 校验后再安装，
# 不执行任何远端脚本。已经用官方脚本装过 Xray 的机器：二进制和 systemd 服务保持原样，
# 只管理配置。配置来自 templates/xray/config.json，已有配置默认保留。
# 和 sing-box 同机共存：Xray 用 443，sing-box 的 VLESS+Reality 用 444。

XRAY_VERSION="${XRAY_VERSION:-26.10.31}"
XRAY_BIN="${XRAY_BIN:-/usr/local/bin/xray}"
XRAY_CONFIG_DIR="${XRAY_CONFIG_DIR:-/usr/local/etc/xray}"
XRAY_PORT="${XRAY_PORT:-443}"
XRAY_DEST="${XRAY_DEST:-www.samsung.com:443}"
XRAY_SERVER_NAME="${XRAY_SERVER_NAME:-www.samsung.com}"
XRAY_SELFTEST_PORT="${XRAY_SELFTEST_PORT:-11080}"
XRAY_UNIT="/etc/systemd/system/xray.service"

xray_usage() {
    cat <<EOF
Xray 模块 (VLESS + Reality):
  install     安装 Xray，生成配置，启动，输出客户端链接
  upgrade     升级二进制到 ${XRAY_VERSION}（配置不动）
  regen       备份旧配置，重新生成 UUID 和 Reality 密钥
  links       输出客户端链接
  check       配置语法、服务、端口、Reality 握手自检
  status      服务状态
  restart     重启服务

环境变量:
  XRAY_VERSION        版本号，默认 ${XRAY_VERSION}
  XRAY_PORT           监听端口，默认 443
  XRAY_DEST           Reality 借用的站点（含端口），默认 www.samsung.com:443
  XRAY_SERVER_NAME    Reality SNI，默认 www.samsung.com
  XRAY_CONFIG_DIR     配置目录，默认 /usr/local/etc/xray
  XRAY_CONFIG_FORCE=1 备份并替换已有配置（等同 regen）
  SERVER_ADDRESS      手动指定服务器地址（默认自动识别）
EOF
}

# ------------------------------------------------------------------ 工具

xray_bin() {
    local b
    b="$(command -v xray 2>/dev/null || true)"
    [ -z "$b" ] && [ -x "$XRAY_BIN" ] && b="$XRAY_BIN"
    [ -n "$b" ] || return 1
    printf '%s\n' "$b"
}

xray_config_file() { printf '%s/config.json\n' "$XRAY_CONFIG_DIR"; }

# 解析 `xray x25519` 的输出：不同版本字段名不同（Private key / PrivateKey，Public key / Password）。
xray_parse_x25519() {
    local out="$1" which="$2"
    if [ "$which" = "private" ]; then
        printf '%s\n' "$out" | awk -F': *' '$1 == "Private key" || $1 == "PrivateKey" { print $2; exit }'
    else
        printf '%s\n' "$out" | awk -F': *' '$1 == "Public key" || $1 == "Password" || $1 ~ /Public[Kk]ey/ { print $2; exit }'
    fi
}

xray_public_from_private() {
    "$1" x25519 -i "$2" 2>/dev/null | awk -F': *' '$1 == "Public key" || $1 == "Password" || $1 ~ /Public[Kk]ey/ { print $2; exit }'
}

xray_validate() {
    "$1" run -test -config "$2" >/dev/null 2>&1 || "$1" test -c "$2" >/dev/null 2>&1
}

# 读 uuid port sni privateKey shortId，TAB 分隔。
xray_read_fields() {
    have python3 || return 1
    python3 "${VPN_SHELL_DIR}/lib/xray_reality_fields.py" "$1"
}

xray_link() {
    printf 'vless://%s@%s:%s?flow=xtls-rprx-vision&encryption=none&type=tcp&security=reality&sni=%s&fp=chrome&pbk=%s&sid=%s#Xray-REALITY\n' \
        "$1" "$2" "$3" "$4" "$5" "$6"
}

xray_asset_name() {
    case "$(detect_arch)" in
        amd64) echo Xray-linux-64.zip ;;
        arm64) echo Xray-linux-arm64-v8a.zip ;;
        armv7) echo Xray-linux-arm32-v7a.zip ;;
        386) echo Xray-linux-32.zip ;;
    esac
}

# ------------------------------------------------------------------ 安装

# 下载固定版本的发布包，校验 SHA256 通过后才安装二进制。
xray_install_binary() {
    local asset base tmp want got
    asset="$(xray_asset_name)"
    base="https://github.com/XTLS/Xray-core/releases/download/v${XRAY_VERSION#v}"
    tmp="$(mktemp -d "${TMPDIR:-/tmp}/xray.XXXXXX")" || die "无法创建临时目录"

    log "下载 ${asset} (v${XRAY_VERSION#v})"
    download "${base}/${asset}" "${tmp}/${asset}" || {
        rm -rf "$tmp"
        die "下载失败，检查网络或 XRAY_VERSION 是否存在"
    }
    download "${base}/${asset}.dgst" "${tmp}/${asset}.dgst" || {
        rm -rf "$tmp"
        die "下载校验文件失败，拒绝安装未校验的二进制"
    }
    want="$(awk -F'= *' '$1 == "SHA2-256" {print $2; exit}' "${tmp}/${asset}.dgst" | tr -d '[:space:]')"
    [ -n "$want" ] || {
        rm -rf "$tmp"
        die "校验文件里没有 SHA2-256"
    }
    if have sha256sum; then
        got="$(sha256sum "${tmp}/${asset}" | awk '{print $1}')"
    else
        got="$(shasum -a 256 "${tmp}/${asset}" | awk '{print $1}')"
    fi
    if [ "$got" != "$want" ]; then
        rm -rf "$tmp"
        die "SHA256 不匹配（期望 ${want}，实际 ${got}），已中止"
    fi
    log "SHA256 校验通过"

    unzip -q -o "${tmp}/${asset}" xray -d "${tmp}/x" || {
        rm -rf "$tmp"
        die "解压失败"
    }
    # 先写临时文件再替换：服务运行中直接覆盖会报 Text file busy。
    install -m 755 "${tmp}/x/xray" "${XRAY_BIN}.new" && mv -f "${XRAY_BIN}.new" "$XRAY_BIN"
    rm -rf "$tmp"
    "$XRAY_BIN" version >/dev/null 2>&1 || die "Xray 安装后无法运行（架构不匹配？）"
    log "已安装: $("$XRAY_BIN" version | head -n 1)"
}

# 没有 systemd 服务才安装我们自己的；官方脚本装出来的服务保持不动。
xray_install_service() {
    if systemctl cat xray.service >/dev/null 2>&1; then
        return 0
    fi
    id xray >/dev/null 2>&1 || useradd --system --no-create-home --shell /usr/sbin/nologin xray \
        || die "创建系统用户 xray 失败"
    install_template "${TEMPLATE_DIR}/xray/xray.service" "$XRAY_UNIT" 644 \
        "BIN=${XRAY_BIN}" "CONFIG_FILE=$(xray_config_file)"
    systemctl daemon-reload
}

xray_upgrade() {
    require_root
    ensure_cmds curl unzip openssl
    xray_install_binary
    if svc_is_active xray.service; then
        systemctl restart xray.service
    fi
}

xray_install() {
    require_root
    have systemctl || die "需要 systemd"
    ensure_cmds curl unzip openssl python3
    local bin cfg keys uuid priv pub sid

    if [ -x "$XRAY_BIN" ] || command -v xray >/dev/null 2>&1; then
        log "已检测到 Xray: $(xray_bin)（升级用: vpn.sh xray upgrade）"
    else
        xray_install_binary
    fi
    bin="$(xray_bin)" || die "找不到 xray 可执行文件"
    cfg="$(xray_config_file)"
    mkdir -p "$XRAY_CONFIG_DIR"

    if [ -f "$cfg" ] && [ "${XRAY_CONFIG_FORCE:-0}" != "1" ]; then
        log "保留已有配置: ${cfg}（XRAY_CONFIG_FORCE=1 或 vpn.sh xray regen 可重新生成）"
    else
        # 重新生成才需要端口空闲；沿用旧配置时端口本来就是 xray 自己占着。
        assert_port_free tcp "$XRAY_PORT" xray XRAY_PORT
        if [ -f "$cfg" ]; then
            backup_file "$cfg"
            log "旧配置已备份"
        fi
        uuid="$("$bin" uuid)" || die "生成 UUID 失败"
        keys="$("$bin" x25519)" || die "生成 X25519 密钥失败"
        priv="$(xray_parse_x25519 "$keys" private)"
        pub="$(xray_parse_x25519 "$keys" public)"
        [ -n "$priv" ] && [ -n "$pub" ] || die "无法解析 xray x25519 输出: ${keys}"
        sid="$(rand_hex 8)"

        install_template "${TEMPLATE_DIR}/xray/config.json" "$cfg" 600 \
            "PORT=${XRAY_PORT}" "UUID=${uuid}" "DEST=${XRAY_DEST}" "SERVER_NAME=${XRAY_SERVER_NAME}" \
            "PRIVATE_KEY=${priv}" "SHORT_ID=${sid}"
    fi
    xray_install_service

    # 服务用户（我们建的是 xray，官方脚本旧版是 nobody）要能读配置，其他人不行。
    if getent group xray >/dev/null 2>&1 && id xray >/dev/null 2>&1; then
        chown root:xray "$XRAY_CONFIG_DIR" "$cfg"
        chmod 750 "$XRAY_CONFIG_DIR"
        chmod 640 "$cfg"
    else
        chmod 700 "$XRAY_CONFIG_DIR"
    fi

    xray_validate "$bin" "$cfg" || die "Xray 配置校验失败: ${cfg}"

    open_port tcp "$XRAY_PORT"
    svc_enable_restart xray.service || die "配置有效，但服务重启失败: journalctl -u xray"
    remind_security_group

    log "Xray 已就绪: ${cfg}"
    xray_links
}

xray_links() {
    local cfg fields uuid port sni priv sid pub bin addr
    cfg="$(xray_config_file)"
    [ -f "$cfg" ] || die "没有 Xray 配置，先运行: vpn.sh xray install"
    bin="$(xray_bin)" || die "没有找到 xray"
    fields="$(xray_read_fields "$cfg")" || die "配置不是可读取的 VLESS+Reality: ${cfg}（vpn.sh xray regen 重新生成）"
    IFS=$'\t' read -r uuid port sni priv sid <<EOF
$fields
EOF
    pub="$(xray_public_from_private "$bin" "$priv")"
    [ -n "$pub" ] || die "无法由私钥推出公钥"
    addr="$(detect_server_address)" || die "无法识别服务器地址，请设置 SERVER_ADDRESS"
    xray_link "$uuid" "$addr" "$port" "$sni" "$pub" "$sid"
}

# ------------------------------------------------------------------ 自检

xray_check() {
    local bin cfg fields uuid port sni priv sid pub tmp pid code fail=0
    bin="$(xray_bin)" || die "没有找到 xray"
    cfg="$(xray_config_file)"
    [ -f "$cfg" ] || die "缺少配置: ${cfg}"

    log "[1/4] 配置语法"
    if xray_validate "$bin" "$cfg"; then
        echo "OK"
    else
        err "FAIL: 配置校验失败"
        fail=1
    fi

    fields="$(xray_read_fields "$cfg")" || die "配置不是可读取的 VLESS+Reality: ${cfg}"
    IFS=$'\t' read -r uuid port sni priv sid <<EOF
$fields
EOF

    log "[2/4] 服务与监听 (tcp/${port})"
    if have systemctl && systemctl cat xray.service >/dev/null 2>&1; then
        if svc_is_active xray.service; then
            echo "OK: xray.service active"
        else
            err "FAIL: xray.service 未运行 (systemctl status xray)"
            fail=1
        fi
    fi
    if port_listeners tcp "$port" | grep -q .; then
        echo "OK: tcp/${port} 在监听"
    else
        err "FAIL: 没有进程监听 tcp/${port}"
        fail=1
    fi

    pub="$(xray_public_from_private "$bin" "$priv")"
    log "[3/4] Reality 参数"
    if [ -z "$pub" ]; then
        err "FAIL: 无法由私钥推出公钥"
        fail=1
    else
        echo "OK: uuid=${uuid} sni=${sni} sid=${sid}"
        echo "OK: pbk=${pub}"
    fi

    log "[4/4] 本机 Reality 握手（起一个本地客户端，经 SOCKS 访问外网）"
    echo "    进程在跑不代表鉴权成功，这一步才验证服务端 Reality"
    if [ -n "$pub" ]; then
        tmp="$(mktemp "${TMPDIR:-/tmp}/xray-selftest.XXXXXX.json")"
        render_template "${TEMPLATE_DIR}/xray/selftest-client.json" "$tmp" \
            "SOCKS_PORT=${XRAY_SELFTEST_PORT}" "PORT=${port}" "UUID=${uuid}" \
            "SERVER_NAME=${sni}" "PUBLIC_KEY=${pub}" "SHORT_ID=${sid}"
        "$bin" run -config "$tmp" >/dev/null 2>&1 &
        pid=$!
        sleep 2
        if ! kill -0 "$pid" 2>/dev/null; then
            err "FAIL: 自检客户端启动即退出"
            fail=1
        elif have curl; then
            code="$(curl -x "socks5h://127.0.0.1:${XRAY_SELFTEST_PORT}" -m 15 -sS -o /dev/null -w '%{http_code}' \
                http://www.gstatic.com/generate_204 2>/dev/null || echo 000)"
            if [ "$code" = "204" ] || [ "$code" = "200" ]; then
                echo "OK: 经 Reality 访问 gstatic 返回 HTTP ${code}"
            else
                err "FAIL: 自检 HTTP 状态 ${code}（期望 204），Reality 入站异常"
                fail=1
            fi
        else
            warn "没有 curl，跳过 HTTP 自检"
        fi
        kill "$pid" 2>/dev/null || true
        wait "$pid" 2>/dev/null || true
        rm -f "$tmp"
    fi

    if [ "$fail" -eq 0 ]; then
        log "服务端检查通过。客户端用上面的链接仍打不开，问题在客户端导入或 Xray 版本太旧"
        return 0
    fi
    err "服务端存在问题，见上方 FAIL"
    return 1
}

xray_main() {
    local action="${1:-}"
    [ $# -gt 0 ] && shift
    case "$action" in
        install) xray_install ;;
        upgrade) xray_upgrade ;;
        regen) XRAY_CONFIG_FORCE=1 xray_install ;;
        links) xray_links ;;
        check) xray_check ;;
        status) systemctl status xray --no-pager -l ;;
        restart) require_root && systemctl restart xray ;;
        '' | help | -h | --help) xray_usage ;;
        *)
            err "未知动作: ${action}"
            xray_usage
            return 2
            ;;
    esac
}
