#!/usr/bin/env bash
# 通用函数库，只被 source，不直接执行。
#
# 约定：
#   - 致命错误用 die（直接退出）；可恢复的失败 return 非 0。
#   - 需要 root 的动作由调用方先 require_root。
#   - 配置内容不写在脚本里：统一放在 ${TEMPLATE_DIR}，用 {{KEY}} 占位，render_template 渲染。
#   - 不用 sed -i（macOS 与 Linux 参数不同），也不用 bash 4 以上才有的语法，方便本机测试。

[ -n "${VPN_COMMON_LOADED:-}" ] && return 0
VPN_COMMON_LOADED=1

VPN_SHELL_DIR="${VPN_SHELL_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
MYCONF_HOME="${MYCONF_HOME:-$(cd "${VPN_SHELL_DIR}/.." && pwd)}"
TEMPLATE_DIR="${VPN_TEMPLATE_DIR:-${MYCONF_HOME}/templates}"
WORKDIR="${VPN_WORKDIR:-/root/work}"
TMP_HOME="${VPN_TMP_HOME:-/root/soft}"

# ------------------------------------------------------------------ 日志

if [ -t 1 ] && [ -z "${NO_COLOR:-}" ]; then
    C_GREEN=$'\033[32m'
    C_YELLOW=$'\033[33m'
    C_RED=$'\033[31m'
    C_OFF=$'\033[0m'
else
    C_GREEN=""
    C_YELLOW=""
    C_RED=""
    C_OFF=""
fi

log() { printf '%s[%s]%s %s\n' "$C_GREEN" "$(date +%H:%M:%S)" "$C_OFF" "$*"; }
warn() { printf '%s[warn]%s %s\n' "$C_YELLOW" "$C_OFF" "$*" >&2; }
err() { printf '%s[error]%s %s\n' "$C_RED" "$C_OFF" "$*" >&2; }
die() {
    err "$*"
    exit 1
}

have() { command -v "$1" >/dev/null 2>&1; }

# ------------------------------------------------------------------ 权限

require_root() {
    [ "$(id -u)" -eq 0 ] || die "需要 root 权限，请用 root 或 sudo 运行"
}

# 以 root 运行时，旧脚本里的 sudo 直接透传：最小化的 Debian 镜像常常没装 sudo。
if [ "$(id -u)" -eq 0 ]; then
    sudo() { "$@"; }
fi

# ------------------------------------------------------------------ 依赖安装

apt_update_once() {
    [ -n "${_VPN_APT_UPDATED:-}" ] && return 0
    apt-get update || return 1
    _VPN_APT_UPDATED=1
}

# ensure_cmds cmd[:package] ...  命令缺失才安装对应的包（包名省略时与命令同名）。
ensure_cmds() {
    local spec cmd pkg
    local missing=()
    for spec in "$@"; do
        cmd="${spec%%:*}"
        pkg="${spec#*:}"
        have "$cmd" || missing+=("$pkg")
    done
    [ "${#missing[@]}" -eq 0 ] && return 0
    have apt-get || die "缺少依赖: ${missing[*]}。不是 apt 系统，请先手动安装"
    log "安装依赖: ${missing[*]}"
    apt_update_once || die "apt-get update 失败"
    DEBIAN_FRONTEND=noninteractive apt-get install -y "${missing[@]}" || die "依赖安装失败: ${missing[*]}"
}

# ------------------------------------------------------------------ 网络识别

is_public_ipv4() {
    local ip="${1:-}"

    [[ "$ip" =~ ^([0-9]{1,3}\.){3}[0-9]{1,3}$ ]] || return 1
    case "$ip" in
        10.* | 127.* | 0.* | 255.* | 192.168.* | 172.1[6-9].* | 172.2[0-9].* | 172.3[0-1].* | 169.254.*)
            return 1
            ;;
    esac
    return 0
}

# 服务器公网 IPv4。优先级：SERVER_ADDRESS / XRAY_SERVER_ADDRESS 环境变量 > 云厂商元数据 >
# 公网探测 > 默认路由的源地址 > 网卡地址。结果缓存，同一次运行只探测一次。
detect_server_address() {
    local ip="" url

    if [ -n "${SERVER_ADDRESS:-}" ]; then
        printf '%s\n' "$SERVER_ADDRESS"
        return 0
    fi
    if [ -n "${XRAY_SERVER_ADDRESS:-}" ]; then
        printf '%s\n' "$XRAY_SERVER_ADDRESS"
        return 0
    fi
    if [ -n "${_VPN_SERVER_ADDR_CACHE:-}" ]; then
        printf '%s\n' "$_VPN_SERVER_ADDR_CACHE"
        return 0
    fi

    if have curl; then
        for url in \
            "http://100.100.100.200/latest/meta-data/eipv4" \
            "http://100.100.100.200/latest/meta-data/public-ipv4" \
            "http://169.254.169.254/latest/meta-data/public-ipv4" \
            "https://api.ipify.org" \
            "https://ifconfig.me/ip" \
            "https://icanhazip.com"; do
            ip=$(curl -4fsS --connect-timeout 2 --max-time 5 "$url" 2>/dev/null | tr -d '[:space:]')
            if is_public_ipv4 "$ip"; then
                _VPN_SERVER_ADDR_CACHE="$ip"
                printf '%s\n' "$ip"
                return 0
            fi
        done
    fi

    if have ip; then
        ip=$(ip -4 route get 1.1.1.1 2>/dev/null | awk '{for (i = 1; i <= NF; i++) if ($i == "src") { print $(i + 1); exit }}')
        if is_public_ipv4 "$ip"; then
            _VPN_SERVER_ADDR_CACHE="$ip"
            printf '%s\n' "$ip"
            return 0
        fi
    fi

    ip=$(hostname -I 2>/dev/null | awk '{print $1}')
    if is_public_ipv4 "$ip"; then
        _VPN_SERVER_ADDR_CACHE="$ip"
        printf '%s\n' "$ip"
        return 0
    fi

    return 1
}

# 旧名字，strongSwan 部分仍在用。
get_ip() {
    detect_server_address 2>/dev/null || true
}

# 出口网卡：默认路由所在的网卡。可用 VPN_NETDEV 覆盖。
get_netdev() {
    local dev=""

    if [ -n "${VPN_NETDEV:-}" ]; then
        printf '%s\n' "$VPN_NETDEV"
        return
    fi
    if have ip; then
        dev=$(ip -4 route show default 2>/dev/null | awk '{for (i = 1; i <= NF; i++) if ($i == "dev") { print $(i + 1); exit }}')
        if [ -n "$dev" ]; then
            printf '%s\n' "$dev"
            return
        fi
    fi
    printf '%s\n' eth0
}

# 监听地址：有 IPv6 就用 ::（同时收 IPv4 和 IPv6），否则 0.0.0.0。
listen_addr() {
    if [ -e /proc/net/if_inet6 ] \
        && [ "$(cat /proc/sys/net/ipv6/conf/all/disable_ipv6 2>/dev/null || echo 1)" != "1" ]; then
        printf '%s\n' "::"
    else
        printf '%s\n' "0.0.0.0"
    fi
}

# CPU 架构，输出 amd64 / arm64 / armv7 / 386。
detect_arch() {
    case "$(uname -m)" in
        x86_64 | amd64) printf '%s\n' amd64 ;;
        aarch64 | arm64) printf '%s\n' arm64 ;;
        armv7* | armhf) printf '%s\n' armv7 ;;
        i386 | i686) printf '%s\n' 386 ;;
        *) die "不支持的 CPU 架构: $(uname -m)" ;;
    esac
}

# ------------------------------------------------------------------ 下载与随机数

# download <url> <dest>
download() {
    local url="$1" dest="$2"
    if have curl; then
        curl -fsSL --retry 3 --retry-delay 2 --connect-timeout 10 -o "$dest" "$url"
    elif have wget; then
        wget -q --tries=3 -O "$dest" "$url"
    else
        die "需要 curl 或 wget"
    fi
}

# rand_hex <字节数>，输出 2 倍长度的十六进制串。链接和配置里都安全，不含需要转义的字符。
rand_hex() {
    local bytes="${1:-16}"
    if have openssl; then
        openssl rand -hex "$bytes"
    else
        od -An -N"$bytes" -tx1 /dev/urandom | tr -d ' \n'
        echo
    fi
}

gen_uuid() {
    if [ -r /proc/sys/kernel/random/uuid ]; then
        cat /proc/sys/kernel/random/uuid
    elif have uuidgen; then
        uuidgen | tr 'A-F' 'a-f'
    else
        local h
        h="$(rand_hex 16)"
        printf '%s-%s-4%s-a%s-%s\n' "${h:0:8}" "${h:8:4}" "${h:13:3}" "${h:17:3}" "${h:20:12}"
    fi
}

# ------------------------------------------------------------------ 模板

# render_template <模板> <输出文件> [KEY=VALUE ...]
# 把模板里的 {{KEY}} 换成 VALUE。渲染后仍有 {{...}} 说明调用方漏传了参数，直接报错，
# 不会把半成品配置写到服务器上。
render_template() {
    local src="$1" dst="$2"
    shift 2
    local content kv key left

    [ -f "$src" ] || die "缺少模板: $src"
    # bash 5.2 起 ${var//pat/rep} 里的 & 有特殊含义，关掉它。
    shopt -u patsub_replacement 2>/dev/null || true
    content="$(cat "$src")"
    for kv in "$@"; do
        key="${kv%%=*}"
        content="${content//\{\{${key}\}\}/${kv#*=}}"
    done
    left="$(printf '%s\n' "$content" | grep -o '{{[A-Z0-9_]*}}' | sort -u | tr '\n' ' ')"
    [ -z "$left" ] || die "模板 $src 有未替换的占位符: $left"
    printf '%s\n' "$content" >"$dst"
}

backup_file() {
    local path="$1"
    [ -f "$path" ] || return 0
    cp -p "$path" "${path}.bak.$(date +%Y%m%d%H%M%S)"
}

# install_file <源文件> <目标> <权限>  内容有变化才备份旧文件。
install_file() {
    local src="$1" dst="$2" mode="${3:-644}"
    [ -f "$src" ] || die "缺少文件: $src"
    mkdir -p "$(dirname "$dst")"
    if [ -f "$dst" ] && ! cmp -s "$src" "$dst"; then
        backup_file "$dst"
    fi
    install -m "$mode" "$src" "$dst"
}

# install_template <模板> <目标> <权限> [KEY=VALUE ...]
install_template() {
    local src="$1" dst="$2" mode="$3"
    shift 3
    local tmp
    tmp="$(mktemp "${TMPDIR:-/tmp}/vpn-render.XXXXXX")" || die "无法创建临时文件"
    render_template "$src" "$tmp" "$@"
    install_file "$tmp" "$dst" "$mode"
    rm -f "$tmp"
}

# ------------------------------------------------------------------ 端口与防火墙

# port_listeners <tcp|udp> <端口>  打印正在监听的 socket（含进程名），没有则无输出。
port_listeners() {
    local flags="-ltnp"
    [ "$1" = "udp" ] && flags="-lunp"
    have ss || return 0
    ss $flags "sport = :$2" 2>/dev/null | tail -n +2
}

# assert_port_free <tcp|udp> <端口> <允许占用的进程名> <改端口用的环境变量>
# 端口被别的进程占用就退出，并告诉用户占用者和怎么换端口。
assert_port_free() {
    local proto="$1" port="$2" owner="$3" envvar="$4" out
    out="$(port_listeners "$proto" "$port")"
    [ -z "$out" ] && return 0
    if [ -n "$owner" ] && printf '%s\n' "$out" | grep -q "\"$owner\""; then
        return 0
    fi
    err "${proto}/${port} 已被占用:"
    printf '%s\n' "$out" >&2
    die "换一个端口再试: 设置环境变量 ${envvar}=<端口> 后重新运行"
}

# open_port <tcp|udp> <端口>  本机防火墙放行；云厂商安全组需要自己在控制台放行。
open_port() {
    local proto="$1" port="$2"
    if have ufw && ufw status 2>/dev/null | grep -q "Status: active"; then
        ufw allow "${port}/${proto}" >/dev/null && log "ufw 已放行 ${port}/${proto}"
    elif have firewall-cmd && firewall-cmd --state >/dev/null 2>&1; then
        firewall-cmd --permanent --add-port="${port}/${proto}" >/dev/null \
            && firewall-cmd --reload >/dev/null \
            && log "firewalld 已放行 ${port}/${proto}"
    elif have iptables && iptables -S INPUT 2>/dev/null | grep -q '^-P INPUT DROP'; then
        iptables -C INPUT -p "$proto" --dport "$port" -j ACCEPT 2>/dev/null \
            || iptables -I INPUT -p "$proto" --dport "$port" -j ACCEPT
        warn "iptables 默认策略是 DROP，已临时放行 ${port}/${proto}，重启后失效，需自行持久化"
    fi
    _VPN_PORTS_OPENED="${_VPN_PORTS_OPENED:-} ${port}/${proto}"
}

# 提醒云安全组。每次运行只在最后调用一次。
remind_security_group() {
    [ -n "${_VPN_PORTS_OPENED:-}" ] || return 0
    warn "云厂商的安全组/防火墙需要在控制台放行:${_VPN_PORTS_OPENED}"
}

# ensure_rule <iptables|ip6tables> [-t 表] <链> <规则...>  规则不存在才追加，重复运行不会堆叠。
ensure_rule() {
    local bin="$1"
    shift
    local table=()
    if [ "${1:-}" = "-t" ]; then
        table=(-t "$2")
        shift 2
    fi
    have "$bin" || return 0
    "$bin" "${table[@]}" -C "$@" 2>/dev/null || "$bin" "${table[@]}" -A "$@"
}

# ------------------------------------------------------------------ 内核参数与服务

enable_ip_forward() {
    install_template "${TEMPLATE_DIR}/system/98-vpn-forward.conf" /etc/sysctl.d/98-vpn-forward.conf 644
    sysctl -e -p /etc/sysctl.d/98-vpn-forward.conf >/dev/null
}

svc_enable_restart() {
    local name="$1"
    systemctl daemon-reload
    systemctl enable "$name" >/dev/null 2>&1 || true
    systemctl restart "$name"
}

svc_is_active() {
    have systemctl && systemctl is-active --quiet "$1" 2>/dev/null
}
