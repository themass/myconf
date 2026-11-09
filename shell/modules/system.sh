#!/usr/bin/env bash
# 服务器通用准备：依赖、内核参数、BBR、IPsec 的 NAT 规则、监控、诊断。
#
# 用法（通过 vpn.sh 调用）：
#   vpn.sh system init              安装编译 strongSwan 需要的依赖
#   vpn.sh system upgrade [full] [dry-run]   升级系统包
#   vpn.sh system net               内核转发、网络调优、文件句柄数（可重复运行）
#   vpn.sh system bbr               开启 BBR
#   vpn.sh system iptables-ipsec    IPsec 放行端口 + NAT（出口网卡自动识别，可重复运行）
#   vpn.sh system fail2ban | telegraf | rclocal
#   vpn.sh system speed | trace | kernel-check | ip

IPSEC_SUBNET="${IPSEC_SUBNET:-10.0.0.0/24}"
TELEGRAF_VERSION="${TELEGRAF_VERSION:-1.4.2-1}"

system_usage() {
    cat <<EOF
系统模块:
  init               安装依赖（编译 strongSwan 用）
  upgrade [full] [dry-run]
                     升级系统包。默认 apt upgrade；full = dist-upgrade（可能换内核）；
                     dry-run 只模拟。保留旧配置，不自动重启服务
  net              内核转发 + 网络调优 + 文件句柄数，写入 /etc/sysctl.d，可重复运行
  bbr                开启 BBR 拥塞控制（内核 4.9+）
  iptables-ipsec     放行 IPsec 端口并做 NAT，规则已存在则跳过；出口网卡自动识别
  fail2ban           安装 fail2ban，使用 monitor/jail.conf
  telegraf           安装 telegraf ${TELEGRAF_VERSION}，使用 monitor/telegraf.conf
  rclocal            安装 rc.local 及 systemd 服务
  speed              安装 speedtest-cli 并测速
  trace              到广州移动/联通/电信的路由追踪
  kernel-check       检查内核是否带 IPsec/XFRM 所需选项
  ip                 显示识别到的公网地址和出口网卡

环境变量: IPSEC_SUBNET（默认 ${IPSEC_SUBNET}）、VPN_NETDEV（出口网卡）
EOF
}

system_init() {
    require_root
    have apt-get || die "init 只支持 apt 系统"
    mkdir -p "$WORKDIR" "$TMP_HOME"
    apt_update_once || die "apt-get update 失败"
    # strongSwan 编译依赖。已去掉 python2、aptitude、php-pear、libmysqlclient-dev：
    # 新系统上没有这些包，configure 又带了 --disable-mysql，用不到。
    DEBIAN_FRONTEND=noninteractive apt-get install -y \
        build-essential gcc automake autoconf autotools-dev libtool pkg-config gettext perl python3 \
        flex bison gperf bzip2 git unzip curl wget vim sysstat iptables iproute2 net-tools \
        libgmp-dev libssl-dev libcurl4-openssl-dev libpcsclite-dev libpam0g-dev libxml2-dev \
        libsystemd-dev libiptc-dev libip4tc-dev libip6tc-dev \
        || die "依赖安装失败"
}

system_net() {
    require_root
    enable_ip_forward
    install_template "${TEMPLATE_DIR}/system/99-vpn-tuning.conf" /etc/sysctl.d/99-vpn-tuning.conf 644
    # -e：忽略当前内核没有的参数，不让一个未知参数中断整批应用。
    sysctl -e -p /etc/sysctl.d/99-vpn-tuning.conf >/dev/null
    install_template "${TEMPLATE_DIR}/system/limits-vpn.conf" /etc/security/limits.d/99-vpn.conf 644
    log "内核参数已写入 /etc/sysctl.d，文件句柄上限写入 /etc/security/limits.d（重新登录后生效）"
}

system_bbr() {
    require_root
    modprobe tcp_bbr 2>/dev/null || true
    if ! sysctl -n net.ipv4.tcp_available_congestion_control 2>/dev/null | grep -qw bbr; then
        die "当前内核不支持 BBR（需要 4.9 以上）：$(uname -r)"
    fi
    install_template "${TEMPLATE_DIR}/system/99-vpn-bbr.conf" /etc/sysctl.d/99-vpn-bbr.conf 644
    sysctl -e -p /etc/sysctl.d/99-vpn-bbr.conf >/dev/null
    log "拥塞控制: $(sysctl -n net.ipv4.tcp_congestion_control)"
}

# 把规则持久化，否则重启后丢失。
# 没装 iptables-persistent 时自动装（非交互），不再只是提示——否则 IKEv2 的 NAT 规则重启就没了，
# 表现为"连上 VPN 却上不了网"。ufw 在用时由 ufw 自己持久化，这里不插手。
system_persist_rules() {
    if have ufw && ufw status 2>/dev/null | grep -q "Status: active"; then
        log "ufw 在用，防火墙规则由 ufw 持久化"
        return 0
    fi
    if ! have netfilter-persistent && have apt-get; then
        log "安装 iptables-persistent（重启后恢复 NAT 和放行规则）"
        apt_update_once || warn "apt-get update 失败，仍尝试安装"
        # 预先回答 debconf，避免弹出"是否保存当前规则"的交互框。
        echo "iptables-persistent iptables-persistent/autosave_v4 boolean true" | debconf-set-selections 2>/dev/null || true
        echo "iptables-persistent iptables-persistent/autosave_v6 boolean true" | debconf-set-selections 2>/dev/null || true
        DEBIAN_FRONTEND=noninteractive apt-get install -y iptables-persistent >/dev/null 2>&1 \
            || warn "iptables-persistent 安装失败，规则只会保存到文件"
    fi
    if have netfilter-persistent; then
        netfilter-persistent save >/dev/null && log "防火墙规则已持久化 (netfilter-persistent)"
    elif [ -d /etc/iptables ]; then
        iptables-save >/etc/iptables/rules.v4
        have ip6tables-save && ip6tables-save >/etc/iptables/rules.v6
        warn "规则已保存到 /etc/iptables/rules.v4，但没有 iptables-persistent，重启时不会恢复"
    else
        warn "规则没有持久化，重启后会丢失。手动安装 iptables-persistent，或运行: vpn.sh system rclocal"
    fi
}

# 升级系统包。默认只做 apt upgrade（不装新依赖、不删包）；full 做 dist-upgrade（可能换内核）。
# 旧配置文件一律保留（confold），不会弹交互框卡住。dry-run 只模拟，不改任何东西。
system_upgrade() {
    local mode="upgrade" dry=0 arg out
    for arg in "$@"; do
        case "$arg" in
            full) mode="dist-upgrade" ;;
            dry-run | --dry-run | -n) dry=1 ;;
            *) die "未知参数: ${arg}（可选: full、dry-run）" ;;
        esac
    done
    require_root
    have apt-get || die "upgrade 只支持 apt 系统"
    apt_update_once || die "apt-get update 失败"
    if [ "$dry" -eq 1 ]; then
        out="$(apt-get -s "$mode" 2>&1)" || { printf '%s\n' "$out" | tail -n 5; die "模拟失败"; }
        log "模拟 apt-get ${mode}，将会升级/安装的包:"
        printf '%s\n' "$out" | grep -E '^(Inst|Remv) ' | awk '{print "  " $1, $2}' | head -n 60
        printf '%s\n' "$out" | grep -E '^[0-9]+ upgraded' || true
        if printf '%s\n' "$out" | grep -qE '^Inst linux-(image|generic|modules)'; then
            warn "包含内核更新，升级后需要重启才生效"
        fi
        return 0
    fi
    log "apt-get ${mode}（保留旧配置文件，非交互）"
    # NEEDRESTART_MODE=l：只列出需要重启的服务，不自动重启——自动重启会把正在跑的
    # xray / sing-box / strongswan 悄悄断掉。升级完用 vpn.sh health 看状态，手动重启。
    NEEDRESTART_MODE=l DEBIAN_FRONTEND=noninteractive apt-get -y \
        -o Dpkg::Options::=--force-confdef -o Dpkg::Options::=--force-confold "$mode" \
        || die "apt-get ${mode} 失败"
    if [ -f /var/run/reboot-required ]; then
        warn "系统要求重启（内核或核心库有更新）: reboot"
    fi
    log "完成。检查服务状态: bash vpn.sh health"
}

system_iptables_ipsec() {
    require_root
    local dev="${1:-$(get_netdev)}"
    [ -n "$dev" ] || die "无法识别出口网卡，请设置 VPN_NETDEV"
    log "IPsec 防火墙，出口网卡: ${dev}，网段: ${IPSEC_SUBNET}"

    local port
    for port in 500 4500 8080 8081; do
        ensure_rule iptables INPUT -p udp --dport "$port" -j ACCEPT
        open_port udp "$port"
    done
    ensure_rule iptables -t nat POSTROUTING -s "$IPSEC_SUBNET" -o "$dev" -j MASQUERADE
    ensure_rule iptables FORWARD -s "$IPSEC_SUBNET" -j ACCEPT
    ensure_rule iptables FORWARD -d "$IPSEC_SUBNET" -j ACCEPT
    # IPv6 分片的 NAT-T 报文：第一片打标记，后续分片按标记放行。
    ensure_rule ip6tables INPUT -p udp --dport 4500 -m frag --fragfirst -j CONNMARK --set-mark 0x42
    ensure_rule ip6tables INPUT -p udp --dport 4500 -j ACCEPT
    ensure_rule ip6tables INPUT -m frag -m connmark --mark 0x42 -j ACCEPT
    system_persist_rules
    remind_security_group
}

system_fail2ban() {
    require_root
    ensure_cmds fail2ban-client:fail2ban sendmail:sendmail
    install_file "${MYCONF_HOME}/monitor/jail.conf" /etc/fail2ban/jail.conf 644
    svc_enable_restart fail2ban
}

system_telegraf() {
    require_root
    local deb="telegraf_${TELEGRAF_VERSION}_amd64.deb"
    [ "$(detect_arch)" = "amd64" ] || die "telegraf ${TELEGRAF_VERSION} 只有 amd64 安装包"
    mkdir -p "$TMP_HOME"
    download "https://dl.influxdata.com/telegraf/releases/${deb}" "${TMP_HOME}/${deb}" || die "下载 telegraf 失败"
    dpkg -i "${TMP_HOME}/${deb}" || die "telegraf 安装失败"
    install_file "${MYCONF_HOME}/monitor/telegraf.conf" /etc/telegraf/telegraf.conf 644
    svc_enable_restart telegraf
}

system_rclocal() {
    require_root
    install_file "${MYCONF_HOME}/monitor/rc-local.service" /etc/systemd/system/rc-local.service 644
    install_file "${MYCONF_HOME}/monitor/rc.local" /etc/rc.local 755
    systemctl daemon-reload
    systemctl enable rc-local >/dev/null 2>&1 || true
}

system_speed() {
    ensure_cmds speedtest-cli
    speedtest-cli
}

system_trace() {
    ensure_cmds mtr
    local label host
    for pair in "广州移动:gd.189.cn" "广州联通:mall.gd10010.cn" "广州电信:189.cn"; do
        label="${pair%%:*}"
        host="${pair#*:}"
        echo "=== ${label} (${host}) ==="
        mtr -n -r -c 5 "$host"
    done
}

system_kernel_check() {
    local cfg opt
    if [ -r "/boot/config-$(uname -r)" ]; then
        cfg="/boot/config-$(uname -r)"
    elif [ -r /proc/config.gz ]; then
        cfg="$(mktemp "${TMPDIR:-/tmp}/kconfig.XXXXXX")"
        zcat /proc/config.gz >"$cfg"
    else
        die "读不到内核配置（/boot/config-$(uname -r) 或 /proc/config.gz）"
    fi
    for opt in CONFIG_XFRM_USER CONFIG_NET_KEY CONFIG_INET CONFIG_IP_ADVANCED_ROUTER CONFIG_IP_MULTIPLE_TABLES \
        CONFIG_INET_AH CONFIG_INET_ESP CONFIG_INET_IPCOMP CONFIG_INET_XFRM_MODE_TRANSPORT \
        CONFIG_INET_XFRM_MODE_TUNNEL CONFIG_INET_XFRM_MODE_BEET CONFIG_IPV6 CONFIG_INET6_AH CONFIG_INET6_ESP \
        CONFIG_INET6_IPCOMP CONFIG_INET6_XFRM_MODE_TRANSPORT CONFIG_INET6_XFRM_MODE_TUNNEL \
        CONFIG_INET6_XFRM_MODE_BEET CONFIG_IPV6_MULTIPLE_TABLES CONFIG_NETFILTER CONFIG_NETFILTER_XTABLES \
        CONFIG_NETFILTER_XT_MATCH_POLICY; do
        if grep -q "^${opt}=[ym]" "$cfg"; then
            printf 'OK      %s\n' "$opt"
        else
            # 新内核把部分 XFRM 模式选项合并进了核心，缺失不一定是问题，只提示。
            printf 'MISSING %s\n' "$opt"
        fi
    done
}

system_ip() {
    echo "公网地址: $(detect_server_address || echo 未识别)"
    echo "出口网卡: $(get_netdev)"
    echo "监听地址: $(listen_addr)"
}

system_main() {
    local action="${1:-}"
    [ $# -gt 0 ] && shift
    case "$action" in
        init) system_init ;;
        upgrade) system_upgrade "$@" ;;
        net) system_net ;;
        bbr) system_bbr ;;
        iptables-ipsec) system_iptables_ipsec "$@" ;;
        fail2ban) system_fail2ban ;;
        telegraf) system_telegraf ;;
        rclocal) system_rclocal ;;
        speed) system_speed ;;
        trace) system_trace ;;
        kernel-check) system_kernel_check ;;
        ip) system_ip ;;
        '' | help | -h | --help) system_usage ;;
        *)
            err "未知动作: ${action}"
            system_usage
            return 2
            ;;
    esac
}
