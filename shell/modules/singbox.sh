#!/usr/bin/env bash
# sing-box 服务端：VLESS+Reality / VMess+WS / Trojan / Shadowsocks / Hysteria2。
#
# 用法（通过 vpn.sh 调用）：
#   vpn.sh singbox install                 只装二进制和服务
#   vpn.sh singbox add <协议|all>           添加一个协议并输出客户端链接（没装会先装）
#   vpn.sh singbox remove <协议>
#   vpn.sh singbox links | status | check | restart | upgrade | uninstall
#
# 配置结构：/etc/sing-box/conf.d/ 下每个协议一个 JSON，sing-box 用 -C 目录方式合并加载。
# 每个协议的参数（UUID、密钥、密码、端口）保存在 /etc/sing-box/state/<协议>.env，
# 重复运行会沿用，不会让已发出去的链接失效；SB_FORCE=1 才会重新生成。
#
# 默认端口（和 Xray 的 443 错开，可以同机共存）：
#   vless-reality 444/tcp   vmess-ws 8880/tcp   trojan 8443/tcp
#   shadowsocks 8388/tcp+udp   hysteria2 8444/udp

SB_VERSION="${SB_VERSION:-1.13.5}"
SB_BIN="${SB_BIN:-/usr/local/bin/sing-box}"
SB_ETC="${SB_ETC:-/etc/sing-box}"
SB_CONF="${SB_ETC}/conf.d"
SB_STATE="${SB_ETC}/state"
SB_CERT_DIR="${SB_ETC}/cert"
SB_USER="sing-box"
SB_PROTOCOLS="vless-reality vmess-ws trojan shadowsocks hysteria2"

singbox_usage() {
    cat <<EOF
sing-box 模块:
  install              下载 sing-box ${SB_VERSION} 并注册 systemd 服务（不启动）
  add <协议>           添加协议并输出客户端链接；协议: ${SB_PROTOCOLS} all
  remove <协议>        删除协议
  links                输出所有已添加协议的客户端链接
  sql [host_v2 行 id]  输出写入后端官方节点列表的 UPDATE 语句
  status               服务状态和监听端口
  check                校验配置并确认各端口在监听
  restart              重启服务
  upgrade              升级到 SB_VERSION（latest 表示最新版）
  uninstall            卸载（SB_PURGE=1 同时删除 ${SB_ETC}）

常用环境变量:
  SB_VERSION           版本号，默认 ${SB_VERSION}
  SB_VLESS_PORT / SB_VMESS_PORT / SB_TROJAN_PORT / SB_SS_PORT / SB_HY2_PORT   端口
  SB_REALITY_DEST      Reality 借用的站点，默认 www.microsoft.com:443
  SB_DOMAIN            有域名时填写，链接和证书用域名
  SB_CERT_FILE / SB_KEY_FILE   已有的正式证书（trojan / hysteria2 用）；不填则自签
  SB_FORCE=1           重新生成该协议的 UUID/密钥/密码
  SERVER_ADDRESS       手动指定服务器地址（默认自动识别）
EOF
}

# ------------------------------------------------------------------ 协议参数

sb_valid_proto() {
    local p
    for p in $SB_PROTOCOLS; do
        [ "$p" = "$1" ] && return 0
    done
    return 1
}

sb_default_port() {
    case "$1" in
        vless-reality) echo 444 ;;
        vmess-ws) echo 8880 ;;
        trojan) echo 8443 ;;
        shadowsocks) echo 8388 ;;
        hysteria2) echo 8444 ;;
    esac
}

sb_port_envvar() {
    case "$1" in
        vless-reality) echo SB_VLESS_PORT ;;
        vmess-ws) echo SB_VMESS_PORT ;;
        trojan) echo SB_TROJAN_PORT ;;
        shadowsocks) echo SB_SS_PORT ;;
        hysteria2) echo SB_HY2_PORT ;;
    esac
}

sb_conf_name() {
    case "$1" in
        vless-reality) echo 10-vless-reality.json ;;
        vmess-ws) echo 20-vmess-ws.json ;;
        trojan) echo 30-trojan.json ;;
        shadowsocks) echo 40-shadowsocks.json ;;
        hysteria2) echo 50-hysteria2.json ;;
    esac
}

# ------------------------------------------------------------------ 状态文件

sb_state_file() { printf '%s/%s.env\n' "$SB_STATE" "$1"; }

# sb_get <协议> <KEY>  取不到输出空。
sb_get() {
    local f
    f="$(sb_state_file "$1")"
    [ -f "$f" ] || return 0
    grep "^$2=" "$f" | head -n 1 | cut -d= -f2-
}

# sb_save <协议> KEY=VALUE ...  整体重写。值里不能有空白、引号等，上游生成的都是安全字符。
sb_save() {
    local proto="$1" kv
    shift
    for kv in "$@"; do
        case "${kv#*=}" in
            *[[:space:]\"\'\\\$\`]*) die "状态值含非法字符，已拒绝写入: ${kv%%=*}" ;;
        esac
    done
    mkdir -p "$SB_STATE"
    (
        umask 077
        printf '%s\n' "$@" >"$(sb_state_file "$proto")"
    )
}

# ------------------------------------------------------------------ 安装

sb_installed() { [ -x "$SB_BIN" ]; }

download_stdout() {
    if have curl; then
        curl -fsSL --retry 3 --connect-timeout 10 "$1"
    else
        wget -qO- --tries=3 "$1"
    fi
}

sb_resolve_version() {
    local ver="$SB_VERSION" tag
    if [ "$ver" = "latest" ]; then
        tag="$(download_stdout "https://api.github.com/repos/SagerNet/sing-box/releases/latest" \
            | grep -m1 '"tag_name"' | sed 's/.*"tag_name"[^"]*"\([^"]*\)".*/\1/')"
        [ -n "$tag" ] || die "查询最新版本失败，请用 SB_VERSION=1.13.5 指定版本"
        ver="$tag"
    fi
    printf '%s\n' "${ver#v}"
}

sb_prepare_system() {
    if ! id "$SB_USER" >/dev/null 2>&1; then
        useradd --system --home-dir /var/lib/sing-box --shell /usr/sbin/nologin "$SB_USER" \
            || die "创建系统用户 ${SB_USER} 失败"
    fi
    mkdir -p "$SB_CONF" "$SB_STATE" "$SB_CERT_DIR"
    # conf.d 里的文件含密码和私钥：root 可写，服务用户只读，其他人不可见。
    chown root:"$SB_USER" "$SB_ETC" "$SB_CONF" "$SB_CERT_DIR"
    chmod 750 "$SB_ETC" "$SB_CONF" "$SB_CERT_DIR"
    chown root:root "$SB_STATE"
    chmod 700 "$SB_STATE"

    install_template "${TEMPLATE_DIR}/singbox/00-base.json" "${SB_CONF}/00-base.json" 640
    chown root:"$SB_USER" "${SB_CONF}/00-base.json"
    install_template "${TEMPLATE_DIR}/singbox/sing-box.service" /etc/systemd/system/sing-box.service 644 \
        "BIN=${SB_BIN}" "CONF_DIR=${SB_CONF}"
    systemctl daemon-reload
    systemctl enable sing-box >/dev/null 2>&1 || true
}

sb_install() {
    require_root
    have systemctl || die "需要 systemd"
    ensure_cmds curl tar openssl

    local ver current arch url tmp bin
    ver="$(sb_resolve_version)"
    current=""
    if sb_installed; then
        current="$("$SB_BIN" version 2>/dev/null | awk 'NR==1 {print $3}')"
    fi

    if [ "$current" = "$ver" ] && [ "${SB_FORCE:-0}" != "1" ]; then
        log "sing-box ${ver} 已安装，跳过下载"
    else
        arch="$(detect_arch)"
        url="https://github.com/SagerNet/sing-box/releases/download/v${ver}/sing-box-${ver}-linux-${arch}.tar.gz"
        tmp="$(mktemp -d "${TMPDIR:-/tmp}/singbox.XXXXXX")" || die "无法创建临时目录"
        log "下载 ${url}"
        download "$url" "${tmp}/sb.tar.gz" || {
            rm -rf "$tmp"
            die "下载失败，检查网络或 SB_VERSION 是否存在"
        }
        tar -xzf "${tmp}/sb.tar.gz" -C "$tmp" || {
            rm -rf "$tmp"
            die "解压失败"
        }
        bin="$(find "$tmp" -type f -name sing-box | head -n 1)"
        [ -n "$bin" ] || {
            rm -rf "$tmp"
            die "压缩包里没有找到 sing-box 可执行文件"
        }
        # 先写临时文件再替换：服务正在运行时直接覆盖会报 Text file busy。
        install -m 755 "$bin" "${SB_BIN}.new" && mv -f "${SB_BIN}.new" "$SB_BIN"
        rm -rf "$tmp"
        "$SB_BIN" version >/dev/null 2>&1 || die "sing-box 安装后无法运行（架构不匹配？）"
        log "已安装: $("$SB_BIN" version | head -n 1)"
    fi
    sb_prepare_system
}

sb_upgrade() {
    sb_installed || die "尚未安装，先运行: vpn.sh singbox install"
    SB_FORCE=1 sb_install
    if svc_is_active sing-box; then
        sb_restart
    fi
}

sb_uninstall() {
    require_root
    systemctl stop sing-box 2>/dev/null || true
    systemctl disable sing-box 2>/dev/null || true
    rm -f /etc/systemd/system/sing-box.service "$SB_BIN"
    systemctl daemon-reload 2>/dev/null || true
    if [ "${SB_PURGE:-0}" = "1" ]; then
        rm -rf "$SB_ETC" /var/lib/sing-box
        log "已卸载并删除 ${SB_ETC}"
    else
        log "已卸载；配置保留在 ${SB_ETC}（SB_PURGE=1 可一并删除）"
    fi
}

# ------------------------------------------------------------------ 运行

sb_restart() {
    systemctl restart sing-box
    sleep 1
    if ! svc_is_active sing-box; then
        err "sing-box 启动失败，最近日志:"
        journalctl -u sing-box --no-pager -n 30 >&2 || true
        return 1
    fi
}

# sb_stage_apply <协议> <渲染好的文件>
# 先把所有配置放进临时目录整体校验，通过了才写入 conf.d，避免坏配置让服务起不来。
sb_stage_apply() {
    local proto="$1" rendered="$2" name stage
    name="$(sb_conf_name "$proto")"
    stage="$(mktemp -d "${TMPDIR:-/tmp}/singbox-stage.XXXXXX")" || die "无法创建临时目录"
    cp "${SB_CONF}"/*.json "$stage"/ 2>/dev/null || true
    cp "$rendered" "${stage}/${name}"
    if ! "$SB_BIN" check -C "$stage"; then
        rm -rf "$stage"
        die "sing-box 配置校验失败，未写入: ${proto}"
    fi
    rm -rf "$stage"
    install_file "$rendered" "${SB_CONF}/${name}" 640
    chown root:"$SB_USER" "${SB_CONF}/${name}"
}

# 端口：环境变量 > 已保存 > 默认值。
sb_resolve_port() {
    local proto="$1" envvar val
    envvar="$(sb_port_envvar "$proto")"
    eval "val=\${${envvar}:-}"
    [ -n "$val" ] || val="$(sb_get "$proto" PORT)"
    [ -n "$val" ] || val="$(sb_default_port "$proto")"
    case "$val" in
        '' | *[!0-9]*) die "端口不是数字: ${envvar}=${val}" ;;
    esac
    [ "$val" -ge 1 ] && [ "$val" -le 65535 ] || die "端口超出范围: ${val}"
    printf '%s\n' "$val"
}

# 同一台机器上其他协议已经用了这个端口就拒绝。
sb_assert_port_unique() {
    local proto="$1" port="$2" other f p
    for other in $SB_PROTOCOLS; do
        [ "$other" = "$proto" ] && continue
        f="$(sb_state_file "$other")"
        [ -f "$f" ] || continue
        p="$(sb_get "$other" PORT)"
        [ "$p" = "$port" ] && die "端口 ${port} 已分配给 ${other}，请用 $(sb_port_envvar "$proto") 换一个"
    done
    return 0
}

sb_check_port_free() {
    local proto="$1" port="$2" net
    net="tcp"
    case "$proto" in
        hysteria2) net="udp" ;;
    esac
    assert_port_free "$net" "$port" sing-box "$(sb_port_envvar "$proto")"
    if [ "$proto" = "shadowsocks" ]; then
        assert_port_free udp "$port" sing-box "$(sb_port_envvar "$proto")"
    fi
}

sb_open_ports() {
    local proto="$1" port="$2"
    case "$proto" in
        hysteria2) open_port udp "$port" ;;
        shadowsocks)
            open_port tcp "$port"
            open_port udp "$port"
            ;;
        *) open_port tcp "$port" ;;
    esac
}

sb_begin() {
    local proto="$1"
    require_root
    sb_installed || sb_install
    [ -d "$SB_CONF" ] || sb_prepare_system
    if [ "${SB_FORCE:-0}" = "1" ]; then
        rm -f "$(sb_state_file "$proto")"
    fi
}

# 写入后统一收尾：放行端口、重启、输出链接。
sb_finish() {
    local proto="$1" port="$2"
    sb_open_ports "$proto" "$port"
    sb_restart || return 1
    remind_security_group
    log "${proto} 已启用（端口 ${port}），客户端链接:"
    sb_link "$proto"
}

# ------------------------------------------------------------------ 证书

# 设置 SB_CERT_PATH SB_KEY_PATH SB_SNI SB_INSECURE SB_HOST。
sb_ensure_cert() {
    local host san crt key
    host="${SB_DOMAIN:-}"
    if [ -z "$host" ]; then
        host="$(detect_server_address)" || die "无法识别服务器地址，请设置 SERVER_ADDRESS 或 SB_DOMAIN"
    fi
    SB_HOST="$host"
    SB_SNI="$host"

    if [ -n "${SB_CERT_FILE:-}" ] || [ -n "${SB_KEY_FILE:-}" ]; then
        [ -f "${SB_CERT_FILE:-}" ] && [ -f "${SB_KEY_FILE:-}" ] || die "SB_CERT_FILE / SB_KEY_FILE 必须同时给出且文件存在"
        [ -n "${SB_DOMAIN:-}" ] || die "使用正式证书时必须设置 SB_DOMAIN（证书对应的域名）"
        SB_CERT_PATH="$SB_CERT_FILE"
        SB_KEY_PATH="$SB_KEY_FILE"
        SB_INSECURE=0
        if have runuser && ! runuser -u "$SB_USER" -- test -r "$SB_KEY_PATH"; then
            warn "服务用户 ${SB_USER} 读不了 ${SB_KEY_PATH}，服务会启动失败。把私钥所在目录对 ${SB_USER} 开放读权限，或用 certbot 的 deploy-hook 复制到 ${SB_CERT_DIR}"
        fi
        return 0
    fi

    crt="${SB_CERT_DIR}/server.crt"
    key="${SB_CERT_DIR}/server.key"
    if [ ! -f "$crt" ] || [ ! -f "$key" ] || [ "${SB_FORCE:-0}" = "1" ]; then
        if is_public_ipv4 "$host"; then
            san="IP:${host}"
        else
            san="DNS:${host}"
        fi
        log "生成自签证书（${host}，有效期 10 年）"
        openssl req -x509 -newkey ec -pkeyopt ec_paramgen_curve:prime256v1 -nodes -days 3650 \
            -keyout "$key" -out "$crt" -subj "/CN=${host}" -addext "subjectAltName=${san}" >/dev/null 2>&1 \
            || die "生成自签证书失败（openssl 需要 1.1.1 以上）"
        chown root:"$SB_USER" "$crt" "$key"
        chmod 644 "$crt"
        chmod 640 "$key"
    fi
    SB_CERT_PATH="$crt"
    SB_KEY_PATH="$key"
    SB_INSECURE=1
}

# ------------------------------------------------------------------ 各协议

sb_add_vless_reality() {
    local proto=vless-reality port uuid priv pub sid dest dest_host dest_port sni host keys tmp
    sb_begin "$proto"
    port="$(sb_resolve_port "$proto")"
    sb_assert_port_unique "$proto" "$port"
    sb_check_port_free "$proto" "$port"

    uuid="$(sb_get "$proto" UUID)"
    priv="$(sb_get "$proto" PRIVATE_KEY)"
    pub="$(sb_get "$proto" PUBLIC_KEY)"
    sid="$(sb_get "$proto" SHORT_ID)"
    dest="${SB_REALITY_DEST:-$(sb_get "$proto" DEST)}"
    dest="${dest:-www.microsoft.com:443}"
    [ -n "$uuid" ] || uuid="$(gen_uuid)"
    [ -n "$sid" ] || sid="$(rand_hex 8)"
    if [ -z "$priv" ] || [ -z "$pub" ]; then
        keys="$("$SB_BIN" generate reality-keypair)" || die "生成 Reality 密钥失败"
        priv="$(printf '%s\n' "$keys" | awk -F': *' '$1 == "PrivateKey" {print $2; exit}')"
        pub="$(printf '%s\n' "$keys" | awk -F': *' '$1 == "PublicKey" {print $2; exit}')"
        [ -n "$priv" ] && [ -n "$pub" ] || die "无法解析 Reality 密钥输出: ${keys}"
    fi
    dest_host="${dest%:*}"
    dest_port="${dest##*:}"
    [ "$dest_host" != "$dest" ] || dest_port=443
    sni="${SB_REALITY_SNI:-$dest_host}"
    host="${SB_DOMAIN:-$(detect_server_address)}" || die "无法识别服务器地址，请设置 SERVER_ADDRESS"

    tmp="$(mktemp "${TMPDIR:-/tmp}/sb-render.XXXXXX")"
    render_template "${TEMPLATE_DIR}/singbox/vless-reality.json" "$tmp" \
        "LISTEN=$(listen_addr)" "PORT=${port}" "UUID=${uuid}" "SNI=${sni}" \
        "DEST_HOST=${dest_host}" "DEST_PORT=${dest_port}" "PRIVATE_KEY=${priv}" "SHORT_ID=${sid}"
    sb_stage_apply "$proto" "$tmp"
    rm -f "$tmp"
    sb_save "$proto" "PORT=${port}" "UUID=${uuid}" "PRIVATE_KEY=${priv}" "PUBLIC_KEY=${pub}" \
        "SHORT_ID=${sid}" "DEST=${dest}" "SNI=${sni}" "HOST=${host}"
    sb_finish "$proto" "$port"
}

sb_add_vmess_ws() {
    local proto=vmess-ws port uuid path host tmp
    sb_begin "$proto"
    port="$(sb_resolve_port "$proto")"
    sb_assert_port_unique "$proto" "$port"
    sb_check_port_free "$proto" "$port"

    uuid="$(sb_get "$proto" UUID)"
    path="$(sb_get "$proto" WS_PATH)"
    [ -n "$uuid" ] || uuid="$(gen_uuid)"
    [ -n "$path" ] || path="/$(rand_hex 4)"
    host="${SB_DOMAIN:-$(detect_server_address)}" || die "无法识别服务器地址，请设置 SERVER_ADDRESS"

    tmp="$(mktemp "${TMPDIR:-/tmp}/sb-render.XXXXXX")"
    render_template "${TEMPLATE_DIR}/singbox/vmess-ws.json" "$tmp" \
        "LISTEN=$(listen_addr)" "PORT=${port}" "UUID=${uuid}" "WS_PATH=${path}"
    sb_stage_apply "$proto" "$tmp"
    rm -f "$tmp"
    sb_save "$proto" "PORT=${port}" "UUID=${uuid}" "WS_PATH=${path}" "HOST=${host}"
    sb_finish "$proto" "$port"
}

sb_add_trojan() {
    local proto=trojan port password tmp
    sb_begin "$proto"
    port="$(sb_resolve_port "$proto")"
    sb_assert_port_unique "$proto" "$port"
    sb_check_port_free "$proto" "$port"
    sb_ensure_cert

    password="$(sb_get "$proto" PASSWORD)"
    [ -n "$password" ] || password="$(rand_hex 16)"

    tmp="$(mktemp "${TMPDIR:-/tmp}/sb-render.XXXXXX")"
    render_template "${TEMPLATE_DIR}/singbox/trojan.json" "$tmp" \
        "LISTEN=$(listen_addr)" "PORT=${port}" "PASSWORD=${password}" \
        "CERT_PATH=${SB_CERT_PATH}" "KEY_PATH=${SB_KEY_PATH}"
    sb_stage_apply "$proto" "$tmp"
    rm -f "$tmp"
    sb_save "$proto" "PORT=${port}" "PASSWORD=${password}" "HOST=${SB_HOST}" "SNI=${SB_SNI}" "INSECURE=${SB_INSECURE}"
    sb_finish "$proto" "$port"
}

sb_add_shadowsocks() {
    local proto=shadowsocks port password method host tmp
    sb_begin "$proto"
    port="$(sb_resolve_port "$proto")"
    sb_assert_port_unique "$proto" "$port"
    sb_check_port_free "$proto" "$port"

    method="${SB_SS_METHOD:-$(sb_get "$proto" METHOD)}"
    method="${method:-chacha20-ietf-poly1305}"
    password="$(sb_get "$proto" PASSWORD)"
    [ -n "$password" ] || password="$(rand_hex 16)"
    host="${SB_DOMAIN:-$(detect_server_address)}" || die "无法识别服务器地址，请设置 SERVER_ADDRESS"

    tmp="$(mktemp "${TMPDIR:-/tmp}/sb-render.XXXXXX")"
    render_template "${TEMPLATE_DIR}/singbox/shadowsocks.json" "$tmp" \
        "LISTEN=$(listen_addr)" "PORT=${port}" "METHOD=${method}" "PASSWORD=${password}"
    sb_stage_apply "$proto" "$tmp"
    rm -f "$tmp"
    sb_save "$proto" "PORT=${port}" "METHOD=${method}" "PASSWORD=${password}" "HOST=${host}"
    sb_finish "$proto" "$port"
}

sb_add_hysteria2() {
    local proto=hysteria2 port password tmp
    sb_begin "$proto"
    port="$(sb_resolve_port "$proto")"
    sb_assert_port_unique "$proto" "$port"
    sb_check_port_free "$proto" "$port"
    sb_ensure_cert

    password="$(sb_get "$proto" PASSWORD)"
    [ -n "$password" ] || password="$(rand_hex 16)"

    tmp="$(mktemp "${TMPDIR:-/tmp}/sb-render.XXXXXX")"
    render_template "${TEMPLATE_DIR}/singbox/hysteria2.json" "$tmp" \
        "LISTEN=$(listen_addr)" "PORT=${port}" "PASSWORD=${password}" \
        "CERT_PATH=${SB_CERT_PATH}" "KEY_PATH=${SB_KEY_PATH}"
    sb_stage_apply "$proto" "$tmp"
    rm -f "$tmp"
    sb_save "$proto" "PORT=${port}" "PASSWORD=${password}" "HOST=${SB_HOST}" "SNI=${SB_SNI}" "INSECURE=${SB_INSECURE}"
    sb_finish "$proto" "$port"
}

sb_add() {
    local target="${1:-}" p
    [ -n "$target" ] || die "用法: vpn.sh singbox add <${SB_PROTOCOLS// /|}|all>"
    if [ "$target" = "all" ]; then
        for p in $SB_PROTOCOLS; do
            sb_add "$p"
        done
        return 0
    fi
    sb_valid_proto "$target" || die "不支持的协议: ${target}（可选: ${SB_PROTOCOLS}）"
    case "$target" in
        vless-reality) sb_add_vless_reality ;;
        vmess-ws) sb_add_vmess_ws ;;
        trojan) sb_add_trojan ;;
        shadowsocks) sb_add_shadowsocks ;;
        hysteria2) sb_add_hysteria2 ;;
    esac
}

sb_remove() {
    local proto="${1:-}"
    sb_valid_proto "$proto" || die "用法: vpn.sh singbox remove <${SB_PROTOCOLS// /|}>"
    require_root
    rm -f "${SB_CONF}/$(sb_conf_name "$proto")" "$(sb_state_file "$proto")"
    if svc_is_active sing-box; then
        sb_restart
    fi
    log "已删除 ${proto}"
}

# ------------------------------------------------------------------ 链接

sb_urlencode() {
    local s="$1" out="" i c
    for ((i = 0; i < ${#s}; i++)); do
        c="${s:i:1}"
        case "$c" in
            [a-zA-Z0-9.~_-]) out+="$c" ;;
            *) out+="$(printf '%%%02X' "'$c")" ;;
        esac
    done
    printf '%s\n' "$out"
}

sb_b64() { printf '%s' "$1" | base64 | tr -d '\n'; }

sb_node_name() {
    sb_urlencode "$(hostname -s 2>/dev/null || echo vpn)-$1"
}

sb_link() {
    local proto="$1" host port name insecure json
    [ -f "$(sb_state_file "$proto")" ] || return 0
    host="$(sb_get "$proto" HOST)"
    port="$(sb_get "$proto" PORT)"
    name="$(sb_node_name "$proto")"
    case "$proto" in
        vless-reality)
            printf 'vless://%s@%s:%s?encryption=none&flow=xtls-rprx-vision&type=tcp&security=reality&sni=%s&fp=chrome&pbk=%s&sid=%s#%s\n' \
                "$(sb_get "$proto" UUID)" "$host" "$port" "$(sb_get "$proto" SNI)" \
                "$(sb_get "$proto" PUBLIC_KEY)" "$(sb_get "$proto" SHORT_ID)" "$name"
            ;;
        vmess-ws)
            json="{\"v\":\"2\",\"ps\":\"$(hostname -s 2>/dev/null || echo vpn)-vmess-ws\",\"add\":\"${host}\",\"port\":\"${port}\",\"id\":\"$(sb_get "$proto" UUID)\",\"aid\":\"0\",\"scy\":\"auto\",\"net\":\"ws\",\"type\":\"none\",\"host\":\"\",\"path\":\"$(sb_get "$proto" WS_PATH)\",\"tls\":\"\"}"
            printf 'vmess://%s\n' "$(sb_b64 "$json")"
            ;;
        trojan)
            insecure=""
            [ "$(sb_get "$proto" INSECURE)" = "1" ] && insecure="&insecure=1"
            printf 'trojan://%s@%s:%s?security=tls&sni=%s%s#%s\n' \
                "$(sb_get "$proto" PASSWORD)" "$host" "$port" "$(sb_get "$proto" SNI)" "$insecure" "$name"
            ;;
        shadowsocks)
            printf 'ss://%s@%s:%s#%s\n' \
                "$(sb_b64 "$(sb_get "$proto" METHOD):$(sb_get "$proto" PASSWORD)" | tr -d '=')" "$host" "$port" "$name"
            ;;
        hysteria2)
            insecure=""
            [ "$(sb_get "$proto" INSECURE)" = "1" ] && insecure="&insecure=1"
            printf 'hysteria2://%s@%s:%s?sni=%s%s#%s\n' \
                "$(sb_get "$proto" PASSWORD)" "$host" "$port" "$(sb_get "$proto" SNI)" "$insecure" "$name"
            ;;
    esac
}

sb_links() {
    local p found=0
    for p in $SB_PROTOCOLS; do
        if [ -f "$(sb_state_file "$p")" ]; then
            found=1
            printf '%s:\n  ' "$p"
            sb_link "$p"
        fi
    done
    [ "$found" -eq 1 ] || warn "还没有添加任何协议，先运行: vpn.sh singbox add <协议>"
}

# ------------------------------------------------------------------ 官方节点列表

# 打印写入后端 host_v2 的 UPDATE 语句（协议名和 proxyLinks，见后端 2026111100_proxy_links.sql）。
# 脚本里的 vmess-ws 在后端和客户端里统一叫 vmess。
sb_sql() {
    local host_id="${1:-<host_v2 的行 id>}" p name names="" json="" sep=""
    for p in $SB_PROTOCOLS; do
        [ -f "$(sb_state_file "$p")" ] || continue
        name="$p"
        [ "$p" = "vmess-ws" ] && name="vmess"
        names="${names}${names:+,}${name}"
        json="${json}${sep}\"${name}\":\"$(sb_link "$p")\""
        sep=","
    done
    [ -n "$names" ] || die "还没有添加任何协议，先运行: vpn.sh singbox add <协议>"
    cat <<EOF
-- 在后端 MySQL 上执行（需要先执行 2026111100_proxy_links.sql）。
-- 代理协议要放在单独的节点行上，protocols 里不要写 ikev2，否则客户端不会使用这些链接。
UPDATE vpn.host_v2
SET protocols  = '${names}',
    proxyLinks = '{${json}}',
    needPing   = 0
WHERE id = ${host_id};
EOF
}

# ------------------------------------------------------------------ 状态与检查

sb_status() {
    systemctl status sing-box --no-pager -l 2>/dev/null | head -n 12 || true
    echo "--- 监听端口 ---"
    if have ss; then
        ss -lntup 2>/dev/null | grep sing-box || echo "(没有 sing-box 监听)"
    fi
}

sb_check() {
    local p port net fail=0
    sb_installed || die "尚未安装"
    log "校验配置"
    "$SB_BIN" check -C "$SB_CONF" || fail=1
    for p in $SB_PROTOCOLS; do
        [ -f "$(sb_state_file "$p")" ] || continue
        port="$(sb_get "$p" PORT)"
        net=tcp
        [ "$p" = "hysteria2" ] && net=udp
        if port_listeners "$net" "$port" | grep -q sing-box; then
            log "OK   ${p} 监听 ${net}/${port}"
        else
            err "FAIL ${p} 没有在监听 ${net}/${port}"
            fail=1
        fi
    done
    return "$fail"
}

singbox_main() {
    local action="${1:-}"
    [ $# -gt 0 ] && shift
    case "$action" in
        install) sb_install ;;
        add) sb_add "$@" ;;
        remove) sb_remove "$@" ;;
        links) sb_links ;;
        sql) sb_sql "$@" ;;
        status) sb_status ;;
        check) sb_check ;;
        restart) require_root && sb_restart ;;
        upgrade) sb_upgrade ;;
        uninstall) sb_uninstall ;;
        '' | help | -h | --help) singbox_usage ;;
        *)
            err "未知动作: ${action}"
            singbox_usage
            return 2
            ;;
    esac
}
