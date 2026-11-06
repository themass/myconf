#!/usr/bin/env bash
# WireGuard 服务端。
#
# 用法（通过 vpn.sh 调用）：
#   vpn.sh wireguard install
#   WG_LEVEL=<线路等级> vpn.sh wireguard sync-install   安装每分钟一次的定时同步（需要 WG_SYNC_URL、WG_SYNC_TOKEN、WG_LEVEL）
#   vpn.sh wireguard sync                    立即从后端同步一次
#   vpn.sh wireguard add-peer <名字> [客户端公钥]   手工添加（地址落在保留段 10.66.255.0/24）
#   vpn.sh wireguard del-peer <名字>
#   vpn.sh wireguard list | info | status | restart | uninstall
#
# 地址规划（所有 WireGuard 节点共用，必须与后端 WgAddress.java 的 PREFIX 一致）：
#   10.66.0.0/16            整个内网
#   10.66.0.1               本节点接口地址
#   10.66.0.2 ~ 10.66.254.255   App 设备，由后端注册时分配，经 sync 写入
#   10.66.255.0/24          手工 peer 专用，自动分配不会落进来
#
# 文件布局（/etc/wireguard）：
#   server.key / server.pub     服务端密钥
#   wg0.base.conf               [Interface] 段，由 templates/wireguard/wg0.base.conf 渲染
#   peers.d/_synced.conf        后端同步来的全部 App 设备（自动生成，不要手改）
#   peers.d/<名字>.conf          手工添加的 peer
#   wg0.conf                    = wg0.base.conf + peers.d/*.conf，每次变动后重新生成
#   sync.env                    同步地址和令牌，权限 600
# wg-quick 不支持 include，所以拼接成完整的 wg0.conf；运行中的接口用 syncconf 热更新，不断开已有连接。

WG_IF="${WG_IF:-wg0}"
WG_ETC="${WG_ETC:-/etc/wireguard}"
WG_PORT="${WG_PORT:-51820}"
WG_SUBNET="${WG_SUBNET:-10.66.0.0/16}"
WG_DNS="${WG_DNS:-1.1.1.1}"
WG_MTU="${WG_MTU:-1420}"
WG_PEERS="${WG_ETC}/peers.d"
WG_SYNCED="${WG_PEERS}/_synced.conf"
WG_SYNC_ENV="${WG_ETC}/sync.env"

wireguard_usage() {
    cat <<EOF
WireGuard 模块:
  install                        安装 wireguard-tools，生成服务端密钥，启动 ${WG_IF}
  sync-install                   安装定时同步：每分钟从后端拉取本线路能用的设备公钥和地址
                                 需要: WG_SYNC_URL=https://api.example.com/vvv/api/noapp/wg/peers.txt
                                       WG_SYNC_TOKEN=<与后端 secrets.properties 的 wg.syncToken 一致>
                                       WG_LEVEL=<本线路等级：0 免费，1/2… 为 VIP>
  sync                           立即同步一次
  add-peer <名字> [客户端公钥]   手工添加；不给公钥则生成密钥并输出完整客户端配置
  del-peer <名字>                删除手工添加的 peer
  list                           列出手工 peer，并显示同步来的设备数量
  info                           服务端公钥、端点、网段（填后端节点的 peerPublicKey 用）
  status                         wg show
  restart                        重新生成 wg0.conf 并重启接口
  uninstall                      停止并禁用接口和定时同步（WG_PURGE=1 同时删除 ${WG_ETC} 下的配置）

环境变量:
  WG_PORT         监听端口，默认 51820/udp
  WG_SUBNET       内网网段，必须是 /16，默认 10.66.0.0/16，要与后端 WgAddress.PREFIX 一致
  WG_DNS / WG_MTU 生成客户端配置时使用，默认 1.1.1.1 / 1420
  WG_BACKEND      auto（默认：内核没有 wireguard 模块时改用 wireguard-go）| kernel | userspace
  WG_SYNC_FORCE=1 同步时允许 peer 数量骤降或清空（默认拒绝，防止后端异常时把所有设备踢掉）
  WG_LEVEL        sync-install 时写入本线路等级；已安装的改线路等级要重新运行 sync-install
  VPN_NETDEV      出口网卡（默认自动识别默认路由所在网卡）
  SERVER_ADDRESS  服务器公网地址（默认自动识别）
EOF
}

# ------------------------------------------------------------------ 网段

# WG_SUBNET 必须是 A.B.0.0/16，返回前两段如 10.66。
wg_prefix() {
    case "$WG_SUBNET" in
        *.*.0.0/16) printf '%s\n' "${WG_SUBNET%.0.0/16}" ;;
        *) die "WG_SUBNET 必须形如 10.66.0.0/16，当前: ${WG_SUBNET}" ;;
    esac
}

wg_server_cidr() { printf '%s.0.1/16\n' "$(wg_prefix)"; }

# 手工 peer 的保留段前缀，如 10.66.255。
wg_manual_prefix() { printf '%s.255\n' "$(wg_prefix)"; }

wg_valid_name() {
    # 首字符必须是字母或数字：下划线开头保留给自动生成的 _synced.conf。
    [[ "$1" =~ ^[A-Za-z0-9][A-Za-z0-9_-]*$ ]]
}

wg_valid_pubkey() {
    # WireGuard 公钥是 32 字节的 base64：44 个字符，以 = 结尾。
    [[ "$1" =~ ^[A-Za-z0-9+/]{43}=$ ]]
}

# 手工 peer 文件（不含自动同步的那个）。
wg_manual_files() {
    local f
    for f in "${WG_PEERS}"/*.conf; do
        [ -f "$f" ] || continue
        [ "$f" = "$WG_SYNCED" ] && continue
        printf '%s\n' "$f"
    done
}

# 下一个空闲的手工地址（保留段 .2 起）。
wg_next_ip() {
    local prefix n used f
    prefix="$(wg_manual_prefix)"
    used=""
    while IFS= read -r f; do
        used="${used}$(sed -n "s/^AllowedIPs = ${prefix//./\\.}\.\([0-9]*\)\/32.*/\1/p" "$f")
"
    done < <(wg_manual_files)
    for ((n = 2; n <= 254; n++)); do
        if ! printf '%s' "$used" | grep -qx "$n"; then
            printf '%s.%s\n' "$prefix" "$n"
            return 0
        fi
    done
    return 1
}

# ------------------------------------------------------------------ 配置生成

wg_rebuild() {
    local conf="${WG_ETC}/${WG_IF}.conf" tmp f
    tmp="$(mktemp "${WG_ETC}/.wgconf.XXXXXX")" || die "无法在 ${WG_ETC} 创建临时文件"
    chmod 600 "$tmp"
    cat "${WG_ETC}/${WG_IF}.base.conf" >"$tmp"
    for f in "${WG_PEERS}"/*.conf; do
        [ -f "$f" ] && cat "$f" >>"$tmp"
    done
    mv -f "$tmp" "$conf"
}

# 接口已经起来就热更新；没起来就启动。
wg_apply() {
    wg_rebuild
    if ip link show "$WG_IF" >/dev/null 2>&1; then
        wg syncconf "$WG_IF" <(wg-quick strip "$WG_IF") || return 1
    else
        systemctl enable "wg-quick@${WG_IF}" >/dev/null 2>&1 || true
        systemctl restart "wg-quick@${WG_IF}" || return 1
    fi
}

wg_endpoint() {
    local addr
    addr="$(detect_server_address)" || die "无法识别服务器地址，请设置 SERVER_ADDRESS"
    printf '%s:%s\n' "$addr" "$WG_PORT"
}

# ------------------------------------------------------------------ 同步：解析与渲染（纯文本处理，可单独测试）

# 校验后端返回的 peer 列表。stdin: 每行 "公钥 10.66.x.y/32"；stdout: 原样输出通过校验的行。
# 任何一行不合法、公钥或地址重复、地址不在自动分配段内，都以非 0 退出——
# 输入来自网络，宁可整批放弃，也不能写入部分数据，更不能让一个 peer 拿到 0.0.0.0/0 之类的宽地址。
wg_sync_parse() {
    awk -v prefix="$(wg_prefix)" '
    function bad(msg) {
        printf "第 %d 行不合法: %s\n", NR, msg > "/dev/stderr"
        failed = 1
        exit 1
    }
    function isnum(s) { return s ~ /^(0|[1-9][0-9]*)$/ }
    NF == 0 { next }
    {
        if (NF != 2) bad("字段数不是 2")
        key = $1
        if (length(key) != 44 || substr(key, 44, 1) != "=" || key !~ /^[A-Za-z0-9+\/]+=$/) bad("公钥格式不对")
        n = split($2, a, /[.\/]/)
        if (n != 5) bad("地址格式不对")
        if (a[1] "." a[2] != prefix) bad("地址不在 " prefix ".0.0/16 内")
        if (!isnum(a[3]) || !isnum(a[4]) || !isnum(a[5])) bad("地址含非数字")
        if (a[5] != 32) bad("必须是 /32")
        if (a[3] + 0 > 254 || a[4] + 0 > 255) bad("地址越界（最后一段保留给手工 peer）")
        if (a[3] * 256 + a[4] < 2) bad("地址不能是网络地址或服务端地址")
        if (key in seen_key) bad("公钥重复")
        if ($2 in seen_addr) bad("地址重复")
        seen_key[key] = 1
        seen_addr[$2] = 1
        print key " " $2
    }
    END { if (failed) exit 1 }
    '
}

# 把校验过的 "公钥 地址" 行渲染成 [Peer] 配置。stdin 为空输出空。
wg_sync_render() {
    awk -v tpl="${TEMPLATE_DIR}/wireguard/peer-synced.conf" '
    function rep(s, from, to,    out, i) {
        out = ""
        while ((i = index(s, from)) > 0) {
            out = out substr(s, 1, i - 1) to
            s = substr(s, i + length(from))
        }
        return out s
    }
    BEGIN {
        while ((getline line < tpl) > 0) t = t line "\n"
        if (t == "") { print "缺少模板: " tpl > "/dev/stderr"; exit 1 }
    }
    {
        s = rep(t, "{{PUBLIC_KEY}}", $1)
        s = rep(s, "{{PEER_ADDRESS}}", $2)
        printf "\n%s", s
    }
    '
}

# 手工 peer 已经用了的公钥，一行一个。
wg_manual_keys() {
    local f
    while IFS= read -r f; do
        sed -n 's/^PublicKey = \(.*\)$/\1/p' "$f"
    done < <(wg_manual_files)
}

# 丢弃公钥在 keys_file（一行一个）里的行，并提示。keys_file 走文件而不是 awk -v：
# 不同 awk 实现对 -v 里的换行处理不一致。
wg_sync_drop_keys() {
    awk -v keysfile="$1" '
    BEGIN { while ((getline k < keysfile) > 0) skip[k] = 1 }
    ($1 in skip) { print "公钥与手工 peer 重复，已跳过同步项: " $1 > "/dev/stderr"; next }
    { print }
    '
}

# 从 sync.env 里读一个值。不 source 这个文件：它是配置，不应该有机会执行代码。
wg_sync_env_get() {
    [ -f "$WG_SYNC_ENV" ] || return 0
    grep "^$1=" "$WG_SYNC_ENV" | head -n 1 | cut -d= -f2-
}

wg_valid_sync_url() {
    # 公网必须 https；http 只允许本机回环（本地调试用），令牌不能走明文跨网络传输。
    [[ "$1" =~ ^https://[A-Za-z0-9.-]+(:[0-9]+)?/[A-Za-z0-9/_.-]*$ ]] \
        || [[ "$1" =~ ^http://(127\.0\.0\.1|localhost)(:[0-9]+)?/[A-Za-z0-9/_.-]*$ ]]
}

wg_valid_level() {
    [[ "$1" =~ ^[0-9]{1,2}$ ]]
}

wg_valid_sync_token() {
    # 限制字符集：令牌会被写进 curl 配置，不能含引号、换行等。
    [[ "$1" =~ ^[A-Za-z0-9._~-]{24,}$ ]]
}

# 拉取后端 peer 列表，输出到 stdout。令牌通过 curl 配置从 stdin 传入，不出现在进程列表里。
wg_sync_fetch() {
    local url="$1" token="$2"
    printf 'header = "X-Sync-Token: %s"\n' "$token" \
        | curl --config - --fail --silent --show-error --max-time 20 --proto '=https,http' \
            --max-filesize 16777216 "$url"
}

# ------------------------------------------------------------------ 同步

wg_sync() {
    require_root
    [ -f "${WG_ETC}/${WG_IF}.base.conf" ] || die "尚未安装，先运行: vpn.sh wireguard install"
    local url token level raw valid new_count old_count tmp
    url="${WG_SYNC_URL:-$(wg_sync_env_get WG_SYNC_URL)}"
    token="${WG_SYNC_TOKEN:-$(wg_sync_env_get WG_SYNC_TOKEN)}"
    level="$(wg_sync_env_get WG_SYNC_LEVEL)"
    [ -n "$url" ] && [ -n "$token" ] && [ -n "$level" ] || die "缺少同步配置（地址、令牌或线路等级），重新运行: WG_LEVEL=<等级> WG_SYNC_URL=... WG_SYNC_TOKEN=... vpn.sh wireguard sync-install"
    wg_valid_sync_url "$url" || die "WG_SYNC_URL 不合法（公网必须 https）: ${url}"
    wg_valid_sync_token "$token" || die "WG_SYNC_TOKEN 不合法（至少 24 位，只允许字母数字和 ._~-）"
    wg_valid_level "$level" || die "WG_SYNC_LEVEL 不合法: ${level}"

    # 定时器和手工运行不能同时改配置。
    if have flock; then
        exec 9>"${WG_ETC}/.sync.lock"
        flock -n 9 || {
            log "上一次同步还在运行，跳过"
            return 0
        }
    fi

    raw="$(wg_sync_fetch "${url}?level=${level}" "$token")" || die "拉取 peer 列表失败（地址、令牌、线路等级或网络有问题）"
    valid="$(printf '%s\n' "$raw" | wg_sync_parse)" || die "后端返回的 peer 列表不合法，已放弃本次同步，配置未改动"

    # 手工 peer 已经占用的公钥：wg 不允许同一个公钥出现两次，丢弃同步来的那条并提示。
    local keys_file
    keys_file="$(mktemp "${TMPDIR:-/tmp}/wg-manual-keys.XXXXXX")" || die "无法创建临时文件"
    wg_manual_keys >"$keys_file"
    if [ -s "$keys_file" ] && [ -n "$valid" ]; then
        valid="$(printf '%s\n' "$valid" | wg_sync_drop_keys "$keys_file")"
    fi
    rm -f "$keys_file"

    new_count=0
    [ -n "$valid" ] && new_count="$(printf '%s\n' "$valid" | wc -l | tr -d ' ')"
    old_count=0
    [ -f "$WG_SYNCED" ] && old_count="$(grep -c '^\[Peer\]' "$WG_SYNCED" || true)"

    # 后端异常（空响应、数据库被清）时不能把线上设备全部踢掉。
    if [ "${WG_SYNC_FORCE:-0}" != "1" ] && [ "$old_count" -gt 0 ]; then
        if [ "$new_count" -eq 0 ] || { [ "$old_count" -ge 10 ] && [ $((new_count * 2)) -lt "$old_count" ]; }; then
            die "peer 数量从 ${old_count} 骤降到 ${new_count}，疑似后端异常，未应用。确认无误后用 WG_SYNC_FORCE=1 重试"
        fi
    fi

    mkdir -p "$WG_PEERS"
    tmp="$(mktemp "${WG_ETC}/.synced.XXXXXX")" || die "无法创建临时文件"
    : >"$tmp"
    if [ -n "$valid" ]; then
        printf '%s\n' "$valid" | wg_sync_render >"$tmp" || {
            rm -f "$tmp"
            die "渲染 peer 配置失败"
        }
    fi
    chmod 600 "$tmp"

    if [ -f "$WG_SYNCED" ] && cmp -s "$tmp" "$WG_SYNCED"; then
        rm -f "$tmp"
        return 0
    fi

    local backup=""
    if [ -f "$WG_SYNCED" ]; then
        backup="$(mktemp "${WG_ETC}/.synced.bak.XXXXXX")"
        cp -p "$WG_SYNCED" "$backup"
    fi
    mv -f "$tmp" "$WG_SYNCED"
    if ! wg_apply; then
        err "应用新配置失败，回滚"
        if [ -n "$backup" ]; then
            mv -f "$backup" "$WG_SYNCED"
        else
            rm -f "$WG_SYNCED"
        fi
        wg_apply || err "回滚后重新应用也失败，请检查: journalctl -u wg-quick@${WG_IF}"
        return 1
    fi
    [ -n "$backup" ] && rm -f "$backup"
    log "已同步: ${old_count} -> ${new_count} 台设备"
}

wg_sync_install() {
    require_root
    have systemctl || die "需要 systemd"
    ensure_cmds curl
    [ -f "${WG_ETC}/${WG_IF}.base.conf" ] || die "尚未安装，先运行: vpn.sh wireguard install"
    local url="${WG_SYNC_URL:-}" token="${WG_SYNC_TOKEN:-}" level="${WG_LEVEL:-}"
    [ -n "$url" ] && [ -n "$token" ] && [ -n "$level" ] || die "需要同时设置 WG_SYNC_URL、WG_SYNC_TOKEN 和 WG_LEVEL"
    wg_valid_sync_url "$url" || die "WG_SYNC_URL 不合法（公网必须 https，形如 https://api.example.com/vvv/api/noapp/wg/peers.txt）"
    wg_valid_sync_token "$token" || die "WG_SYNC_TOKEN 不合法（至少 24 位，只允许字母数字和 ._~-）"
    wg_valid_level "$level" || die "WG_LEVEL 必须是 0~99 的整数（0 为免费线路）"

    install_template "${TEMPLATE_DIR}/wireguard/sync.env" "$WG_SYNC_ENV" 600 \
        "SYNC_URL=${url}" "SYNC_TOKEN=${token}" "SYNC_LEVEL=${level}"
    install_template "${TEMPLATE_DIR}/wireguard/wg-sync.service" /etc/systemd/system/wg-sync.service 644 \
        "SCRIPT=${VPN_SHELL_DIR}/vpn.sh"
    install_file "${TEMPLATE_DIR}/wireguard/wg-sync.timer" /etc/systemd/system/wg-sync.timer 644
    systemctl daemon-reload

    # 先同步一次，成功后才启用定时器：配置有误时不让定时器每分钟失败刷日志。
    # 子 shell 里运行，wg_sync 内部的 die 只退出子 shell，这里可以接住失败。
    log "立即同步一次，成功后才启用定时器:"
    if ! (wg_sync); then
        systemctl disable --now wg-sync.timer >/dev/null 2>&1 || true
        die "首次同步失败，定时器未启用。修正上面的错误后重新运行 sync-install"
    fi
    systemctl enable --now wg-sync.timer >/dev/null
    log "已启用定时同步（每分钟）"
}

# ------------------------------------------------------------------ 动作

# ------------------------------------------------------------------ 后端选择（内核模块 / wireguard-go）

WG_DROPIN="/etc/systemd/system/wg-quick@${WG_IF}.service.d/userspace.conf"

# 内核是否有 wireguard 模块（已加载、可加载，或编译进内核都算）。
wg_kernel_has_module() {
    [ -d /sys/module/wireguard ] && return 0
    modprobe wireguard >/dev/null 2>&1
}

# WG_BACKEND: auto（默认，内核没有模块时用 wireguard-go）、kernel、userspace。
# userspace 通过 systemd drop-in 设置 WG_QUICK_USERSPACE_IMPLEMENTATION=wireguard-go，wg-quick 会自动启动它。
# 返回 0 表示改变了后端（需要重启接口）。
wg_setup_backend() {
    local want="${WG_BACKEND:-auto}" use_userspace=0 before=kernel after
    case "$want" in
        auto | kernel | userspace) ;;
        *) die "WG_BACKEND 只能是 auto、kernel 或 userspace，当前: ${want}" ;;
    esac
    [ -f "$WG_DROPIN" ] && before=userspace

    if [ "$want" = userspace ]; then
        use_userspace=1
    elif [ "$want" = auto ] && ! wg_kernel_has_module; then
        use_userspace=1
    elif [ "$want" = kernel ] && ! wg_kernel_has_module; then
        die "内核没有 wireguard 模块。可安装 wireguard-dkms 或升级内核，或改用 WG_BACKEND=userspace"
    fi

    if [ "$use_userspace" = 1 ]; then
        have wireguard-go || {
            ensure_cmds wireguard-go || die "无法安装 wireguard-go（当前系统的 apt 源可能没有这个包），请手动安装或升级系统"
        }
        install_template "${TEMPLATE_DIR}/wireguard/userspace.conf" "$WG_DROPIN" 644
        after=userspace
        log "WireGuard 使用用户态实现 wireguard-go"
    else
        rm -f "$WG_DROPIN"
        after=kernel
        log "WireGuard 使用内核模块"
    fi
    systemctl daemon-reload

    [ "$before" != "$after" ] && return 0
    return 1
}

wg_install() {
    require_root
    have systemctl || die "需要 systemd"
    ensure_cmds wg:wireguard-tools iptables ip:iproute2
    wg_prefix >/dev/null

    local netdev server_cidr old_addr=""
    netdev="$(get_netdev)"
    server_cidr="$(wg_server_cidr)"
    mkdir -p "$WG_PEERS"
    chmod 700 "$WG_ETC" "$WG_PEERS"
    # 接口已经由本脚本拉起时端口是自己占着的，只在首次安装时检查。
    [ -f "${WG_ETC}/${WG_IF}.base.conf" ] || assert_port_free udp "$WG_PORT" "" WG_PORT
    [ -f "${WG_ETC}/${WG_IF}.base.conf" ] && old_addr="$(sed -n 's/^Address = \(.*\)$/\1/p' "${WG_ETC}/${WG_IF}.base.conf")"

    if [ ! -f "${WG_ETC}/server.key" ]; then
        (
            umask 077
            wg genkey >"${WG_ETC}/server.key"
        )
        wg pubkey <"${WG_ETC}/server.key" >"${WG_ETC}/server.pub"
        log "已生成服务端密钥"
    fi

    enable_ip_forward
    install_template "${TEMPLATE_DIR}/wireguard/wg0.base.conf" "${WG_ETC}/${WG_IF}.base.conf" 600 \
        "SERVER_CIDR=${server_cidr}" "PORT=${WG_PORT}" "SUBNET=${WG_SUBNET}" \
        "NETDEV=${netdev}" "PRIVATE_KEY=$(cat "${WG_ETC}/server.key")"

    # 手工 peer 必须在保留段内，否则会和后端分配的设备地址冲突。
    local f stray
    while IFS= read -r f; do
        stray="$(sed -n 's/^AllowedIPs = \(.*\)$/\1/p' "$f" | grep -v "^$(wg_manual_prefix | sed 's/\./\\./g')\." || true)"
        [ -z "$stray" ] || warn "手工 peer $(basename "$f") 的地址 ${stray} 不在保留段 $(wg_manual_prefix).0/24，可能和设备地址冲突，请 del-peer 后重新添加"
    done < <(wg_manual_files)

    open_port udp "$WG_PORT"
    local backend_changed=0
    wg_setup_backend && backend_changed=1
    # 接口地址变了（比如从旧的 /24 升级到 /16）：syncconf 改不了接口地址，必须重启接口。
    # 后端切换（内核 <-> wireguard-go）同样必须重启。
    if [ "$backend_changed" = 1 ] && ip link show "$WG_IF" >/dev/null 2>&1; then
        warn "WireGuard 后端已切换，重启 ${WG_IF}（已有连接会短暂中断）"
        wg_rebuild
        systemctl restart "wg-quick@${WG_IF}" || die "重启 ${WG_IF} 失败: journalctl -u wg-quick@${WG_IF}"
    elif [ -n "$old_addr" ] && [ "$old_addr" != "$server_cidr" ] && ip link show "$WG_IF" >/dev/null 2>&1; then
        warn "接口地址 ${old_addr} -> ${server_cidr}，重启 ${WG_IF}（已有连接会短暂中断）"
        wg_rebuild
        systemctl restart "wg-quick@${WG_IF}" || die "重启 ${WG_IF} 失败: journalctl -u wg-quick@${WG_IF}"
    else
        wg_apply || die "启动 ${WG_IF} 失败: journalctl -u wg-quick@${WG_IF}"
    fi
    remind_security_group
    log "WireGuard 已启动: ${WG_IF}，出口网卡 ${netdev}"
    wg_info
}

wg_info() {
    [ -f "${WG_ETC}/server.pub" ] || die "尚未安装，先运行: vpn.sh wireguard install"
    echo "服务端公钥: $(cat "${WG_ETC}/server.pub")   <- 填到后端该节点的 peerPublicKey"
    echo "端点:       $(wg_endpoint)"
    echo "网段:       ${WG_SUBNET}（本节点 $(wg_server_cidr)，手工 peer 用 $(wg_manual_prefix).0/24）"
    if systemctl is-active --quiet wg-sync.timer 2>/dev/null; then
        echo "设备同步:   已启用（每分钟，线路等级 $(wg_sync_env_get WG_SYNC_LEVEL)）"
    else
        echo "设备同步:   未启用，App 设备连不上。运行 vpn.sh wireguard sync-install"
    fi
}

wg_add_peer() {
    local name="${1:-}" pubkey="${2:-}" ip client_priv="" tmp
    require_root
    wg_valid_name "$name" || die "用法: vpn.sh wireguard add-peer <名字(字母数字开头，可含 _-)> [客户端公钥]"
    [ -f "${WG_ETC}/server.pub" ] || die "尚未安装，先运行: vpn.sh wireguard install"
    [ ! -f "${WG_PEERS}/${name}.conf" ] || die "客户端 ${name} 已存在，先 del-peer 或换个名字"

    if [ -n "$pubkey" ]; then
        wg_valid_pubkey "$pubkey" || die "公钥格式不对（应为 44 位 base64，以 = 结尾）"
        grep -qs "^PublicKey = ${pubkey}\$" "${WG_PEERS}"/*.conf && die "这个公钥已经登记过"
    else
        client_priv="$(wg genkey)"
        pubkey="$(printf '%s' "$client_priv" | wg pubkey)"
    fi

    ip="$(wg_next_ip)" || die "手工地址已用完（$(wg_manual_prefix).2 ~ .254）"
    install_template "${TEMPLATE_DIR}/wireguard/peer.conf" "${WG_PEERS}/${name}.conf" 600 \
        "NAME=${name}" "PUBLIC_KEY=${pubkey}" "PEER_ADDRESS=${ip}"
    wg_apply || die "应用配置失败: journalctl -u wg-quick@${WG_IF}"

    log "已添加 ${name}，地址 ${ip}"
    if [ -n "$client_priv" ]; then
        echo "---------- 客户端配置（保存为 ${name}.conf，私钥只显示这一次）----------"
        tmp="$(mktemp "${TMPDIR:-/tmp}/wg-client.XXXXXX")"
        render_template "${TEMPLATE_DIR}/wireguard/client.conf" "$tmp" \
            "CLIENT_PRIVATE_KEY=${client_priv}" "PEER_ADDRESS=${ip}" "DNS=${WG_DNS}" "MTU=${WG_MTU}" \
            "SERVER_PUBLIC_KEY=$(cat "${WG_ETC}/server.pub")" "ENDPOINT=$(wg_endpoint)" \
            "ALLOWED_IPS=0.0.0.0/0"
        cat "$tmp"
        if have qrencode; then
            echo "---------- 二维码 ----------"
            qrencode -t ansiutf8 <"$tmp"
        fi
        rm -f "$tmp"
    else
        echo "客户端地址: ${ip}/32"
        echo "服务端公钥: $(cat "${WG_ETC}/server.pub")"
        echo "端点:       $(wg_endpoint)"
    fi
}

wg_del_peer() {
    local name="${1:-}"
    require_root
    wg_valid_name "$name" || die "用法: vpn.sh wireguard del-peer <名字>"
    [ -f "${WG_PEERS}/${name}.conf" ] || die "没有这个手工 peer: ${name}（App 设备由后端管理，不能在这里删）"
    rm -f "${WG_PEERS}/${name}.conf"
    wg_apply || die "应用配置失败: journalctl -u wg-quick@${WG_IF}"
    log "已删除 ${name}"
}

wg_list() {
    local f name ip count=0 synced=0
    while IFS= read -r f; do
        name="$(basename "$f" .conf)"
        ip="$(sed -n 's/^AllowedIPs = \(.*\)$/\1/p' "$f" | head -n 1)"
        printf '%-20s %s\n' "$name" "$ip"
        count=$((count + 1))
    done < <(wg_manual_files)
    [ "$count" -gt 0 ] || echo "(没有手工 peer)"
    [ -f "$WG_SYNCED" ] && synced="$(grep -c '^\[Peer\]' "$WG_SYNCED" || true)"
    echo "后端同步的设备: ${synced} 台"
}

wg_status() {
    wg show "$WG_IF" 2>/dev/null || echo "${WG_IF} 未运行"
}

wg_restart() {
    require_root
    wg_rebuild
    systemctl restart "wg-quick@${WG_IF}" || die "重启失败: journalctl -u wg-quick@${WG_IF}"
}

wg_uninstall() {
    require_root
    systemctl disable --now wg-sync.timer 2>/dev/null || true
    rm -f /etc/systemd/system/wg-sync.service /etc/systemd/system/wg-sync.timer
    systemctl stop "wg-quick@${WG_IF}" 2>/dev/null || true
    systemctl disable "wg-quick@${WG_IF}" 2>/dev/null || true
    rm -f "$WG_DROPIN"
    systemctl daemon-reload 2>/dev/null || true
    if [ "${WG_PURGE:-0}" = "1" ]; then
        rm -rf "$WG_ETC"
        log "已停止并删除 ${WG_ETC}"
    else
        log "已停止；配置和密钥保留在 ${WG_ETC}（WG_PURGE=1 可一并删除）"
    fi
}

wireguard_main() {
    local action="${1:-}"
    [ $# -gt 0 ] && shift
    case "$action" in
        install) wg_install ;;
        sync-install) wg_sync_install ;;
        sync) wg_sync ;;
        add-peer) wg_add_peer "$@" ;;
        del-peer) wg_del_peer "$@" ;;
        list) wg_list ;;
        info) wg_info ;;
        status) wg_status ;;
        restart) wg_restart ;;
        uninstall) wg_uninstall ;;
        '' | help | -h | --help) wireguard_usage ;;
        *)
            err "未知动作: ${action}"
            wireguard_usage
            return 2
            ;;
    esac
}
