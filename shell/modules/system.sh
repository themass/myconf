#!/usr/bin/env bash
# 服务器通用准备：依赖、内核参数、BBR、IPsec 的 NAT 规则、监控、诊断。
#
# 用法（通过 vpn.sh 调用）：
#   vpn.sh system init              安装编译 strongSwan 需要的依赖
#   vpn.sh system upgrade [full] [dry-run]   升级系统包
#   vpn.sh system net               内核转发、网络调优、文件句柄数（可重复运行）
#   vpn.sh system bbr               开启 BBR
#   vpn.sh system firewall [网卡]   所有已装 VPN 的端口 + NAT（端口/网段读实际配置，网卡自动识别，可重复运行）
#   vpn.sh system fail2ban | rclocal
#   vpn.sh system speed | trace | kernel-check | ip

IPSEC_SUBNET="${IPSEC_SUBNET:-10.0.0.0/24}"
IPSEC_SUBNET6="${IPSEC_SUBNET6:-fec3::/120}"

system_usage() {
    cat <<EOF
系统模块:
  init               安装依赖（编译 strongSwan 用）
  upgrade [full] [dry-run]
                     升级系统包。默认 apt upgrade；full = dist-upgrade（可能换内核）；
                     dry-run 只模拟。保留旧配置，不自动重启服务
  net              内核转发 + 网络调优 + 文件句柄数，写入 /etc/sysctl.d，可重复运行
  bbr                开启 BBR 拥塞控制（内核 4.9+）
  firewall [网卡]    所有已装 VPN（IKEv2/WireGuard/Xray/sing-box）的端口放行 + 虚拟网段 NAT
                     端口和网段读各服务的实际配置；网卡、公网 IP 自动识别；删除指向旧网卡的规则
  iptables-ipsec     同 firewall（旧名字）
  fail2ban           安装 fail2ban，使用 conf/system/jail.conf
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
    log "内核参数已立即生效（sysctl -p）。文件句柄上限写入 /etc/security/limits.d，只对新登录会话生效，已开着的 shell 需要重新登录"
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

# ------------------------------------------------------------------ 防火墙

# 本机已装的 VPN 实际在用的端口和虚拟网段，全部从各服务的配置里读，读不到才用默认值。
# 输出每行一项: "<类型> <值>"，类型: port-udp / port-tcp / nat4 / nat6 / ipsec-natt
fw_collect() {
    local f line addrs a ike natt p port wgnet
    # strongSwan：端口取 /etc/strongswan.conf，地址池取 swanctl.conf 的 addrs。
    if [ -f /etc/swanctl/swanctl.conf ] || [ -f /etc/strongswan.conf ]; then
        ike="$(sed -n 's/^[[:space:]]*port[[:space:]]*=[[:space:]]*\([0-9]*\).*/\1/p' /etc/strongswan.conf 2>/dev/null | head -n 1)"
        natt="$(sed -n 's/^[[:space:]]*port_nat_t[[:space:]]*=[[:space:]]*\([0-9]*\).*/\1/p' /etc/strongswan.conf 2>/dev/null | head -n 1)"
        printf 'port-udp %s\nport-udp %s\nipsec-natt %s\n' "${ike:-${SS_IKE_PORT:-8081}}" "${natt:-${SS_NATT_PORT:-8080}}" "${natt:-${SS_NATT_PORT:-8080}}"
        addrs="$(sed -n 's/^[[:space:]]*addrs[[:space:]]*=[[:space:]]*//p' /etc/swanctl/swanctl.conf 2>/dev/null | head -n 1)"
        [ -n "$addrs" ] || addrs="${IPSEC_SUBNET}, ${IPSEC_SUBNET6}"
        for a in $(printf '%s' "$addrs" | tr ',' ' '); do
            case "$a" in *:*) printf 'nat6 %s\n' "$a" ;; *) printf 'nat4 %s\n' "$a" ;; esac
        done
    fi
    # WireGuard：端口取 wg0.conf 的 ListenPort；网段取接口路由（接口没起来就用 WG_SUBNET）。
    f="/etc/wireguard/${WG_IF:-wg0}.conf"
    if [ -f "$f" ]; then
        port="$(sed -n 's/^[[:space:]]*ListenPort[[:space:]]*=[[:space:]]*\([0-9]*\).*/\1/p' "$f" | head -n 1)"
        printf 'port-udp %s\n' "${port:-${WG_PORT:-51820}}"
        wgnet="$(ip -4 route show dev "${WG_IF:-wg0}" scope link 2>/dev/null | awk '{print $1; exit}')"
        printf 'nat4 %s\n' "${wgnet:-${WG_SUBNET:-10.66.0.0/16}}"
    fi
    # Xray：只放端口，代理协议不需要 NAT。
    f="${XRAY_CONFIG_DIR:-/usr/local/etc/xray}/config.json"
    if [ -f "$f" ]; then
        port="$(grep -o '"port"[[:space:]]*:[[:space:]]*[0-9]*' "$f" | head -n 1 | grep -o '[0-9]*$')"
        printf 'port-tcp %s\n' "${port:-${XRAY_PORT:-443}}"
    fi
    # sing-box：每个协议一个 state 文件。
    for f in "${SB_ETC:-/etc/sing-box}"/state/*.env; do
        [ -f "$f" ] || continue
        p="$(basename "$f" .env)"
        port="$(grep '^PORT=' "$f" | head -n 1 | cut -d= -f2-)"
        [ -n "$port" ] || continue
        case "$p" in
            hysteria2) printf 'port-udp %s\n' "$port" ;;
            shadowsocks) printf 'port-tcp %s\nport-udp %s\n' "$port" "$port" ;;
            *) printf 'port-tcp %s\n' "$port" ;;
        esac
    done
}

# 删除指向其它网卡的 MASQUERADE 规则（如镜像或旧 rc.local 留下的 -o ens17）。只删 -o 不等于当前网卡的。
fw_drop_stale_nat() { # <iptables|ip6tables> <网段> <当前网卡>
    local bin="$1" subnet="$2" dev="$3" line
    local parts=()
    have "$bin" || return 0
    "$bin" -t nat -S POSTROUTING 2>/dev/null | grep -F -- "-s ${subnet} " | grep -- "-j MASQUERADE" | grep -- " -o " \
        | while IFS= read -r line; do
            case " $line " in *" -o ${dev} "*) continue ;; esac
            read -r -a parts <<<"$line"
            parts[0]="-D"
            "$bin" -t nat "${parts[@]}" && warn "删除了出口网卡不对的旧规则: ${line}"
        done
}

# 放行所有已装 VPN 的端口，为每个虚拟网段做 NAT 和转发，出口网卡自动识别，规则持久化。可重复运行。
system_firewall() {
    require_root
    local dev="${1:-$(get_netdev)}" kind val ip natt="" has6=0 items
    [ -n "$dev" ] || die "无法识别出口网卡，请设置 VPN_NETDEV"
    ip link show "$dev" >/dev/null 2>&1 || die "出口网卡 ${dev} 不存在（ip link 里没有）。用 VPN_NETDEV=<网卡> 指定"
    ip="$(detect_server_address 2>/dev/null || echo 未识别)"
    ip -6 route show default 2>/dev/null | grep -q . && has6=1
    items="$(fw_collect | sort -u)"
    [ -n "$items" ] || { warn "没有发现已安装的 VPN 服务，跳过防火墙"; return 0; }
    log "防火墙：出口网卡 ${dev}，公网地址 ${ip}"

    while read -r kind val; do
        [ -n "$val" ] || continue
        case "$kind" in
            port-udp | port-tcp)
                ensure_rule iptables INPUT -p "${kind#port-}" --dport "$val" -j ACCEPT
                open_port "${kind#port-}" "$val"
                ;;
            nat4)
                fw_drop_stale_nat iptables "$val" "$dev"
                ensure_rule iptables -t nat POSTROUTING -s "$val" -o "$dev" -j MASQUERADE
                ensure_rule iptables FORWARD -s "$val" -j ACCEPT
                ensure_rule iptables FORWARD -d "$val" -j ACCEPT
                # TCP MSS 固定夹到 VPN_CLAMP_MSS（默认 1240 = 客户端隧道下限 1280 - 40），两个方向都夹。
                # 不用 --clamp-mss-to-pmtu：它按服务器出口网卡（1500）算，得到的 MSS 比客户端通告的还大，等于没夹。
                # --set-mss 只会调小，客户端 MTU 设得更小时不受影响。
                local mss="${VPN_CLAMP_MSS:-1240}"
                # 删掉旧版本留下的 clamp-mss-to-pmtu 规则（同一网段只保留一条生效的 MSS 规则）
                iptables -t mangle -D FORWARD -s "$val" -p tcp --tcp-flags SYN,RST SYN -j TCPMSS --clamp-mss-to-pmtu 2>/dev/null || true
                ensure_rule iptables -t mangle FORWARD -s "$val" -p tcp --tcp-flags SYN,RST SYN -j TCPMSS --set-mss "$mss"
                ensure_rule iptables -t mangle FORWARD -d "$val" -p tcp --tcp-flags SYN,RST SYN -j TCPMSS --set-mss "$mss"
                log "  NAT ${val} -> ${dev}"
                ;;
            nat6)
                # 地址池是 ULA（如 fec3::/120），服务器有 IPv6 默认路由时才做 NAT66，否则客户端的 IPv6 流量出不去。
                if [ "$has6" = 1 ]; then
                    fw_drop_stale_nat ip6tables "$val" "$dev"
                    ensure_rule ip6tables -t nat POSTROUTING -s "$val" -o "$dev" -j MASQUERADE
                    ensure_rule ip6tables FORWARD -s "$val" -j ACCEPT
                    ensure_rule ip6tables FORWARD -d "$val" -j ACCEPT
                    # IPv6 最小 MTU 1280，减 IPv6 头 40、TCP 头 20 = 1220；两个方向都夹
                    local mss6="${VPN_CLAMP_MSS6:-1220}"
                    ensure_rule ip6tables -t mangle FORWARD -s "$val" -p tcp --tcp-flags SYN,RST SYN -j TCPMSS --set-mss "$mss6"
                    ensure_rule ip6tables -t mangle FORWARD -d "$val" -p tcp --tcp-flags SYN,RST SYN -j TCPMSS --set-mss "$mss6"
                    log "  NAT6 ${val} -> ${dev}"
                fi
                ;;
            ipsec-natt) natt="$val" ;;
        esac
    done <<<"$items"

    # IPv6 分片的 NAT-T 报文：第一片打标记，后续分片按标记放行。端口用实际的 NAT-T 端口。
    if [ -n "$natt" ]; then
        ensure_rule ip6tables INPUT -p udp --dport "$natt" -m frag --fragfirst -j CONNMARK --set-mark 0x42
        ensure_rule ip6tables INPUT -p udp --dport "$natt" -j ACCEPT
        ensure_rule ip6tables INPUT -m frag -m connmark --mark 0x42 -j ACCEPT
    fi

    # 旧 rc.local 开机会再加一遍写死网卡的规则，必须换掉，否则重启后又回来。
    if [ -f /etc/rc.local ] && grep -qE 'iptables .*-(A|I) ' /etc/rc.local 2>/dev/null; then
        warn "/etc/rc.local 里还有写死的 iptables 规则，重启后会再加回旧规则。修复: bash vpn.sh system rclocal"
    fi
    # WireGuard 的 PostUp 里网卡名是安装时写进去的，换网卡后要重新渲染。
    if [ -f "/etc/wireguard/${WG_IF:-wg0}.base.conf" ] \
        && grep -q -- "-o " "/etc/wireguard/${WG_IF:-wg0}.base.conf" \
        && ! grep -q -- "-o ${dev} " "/etc/wireguard/${WG_IF:-wg0}.base.conf"; then
        warn "WireGuard 配置里的出口网卡不是 ${dev}。修复: bash vpn.sh wireguard install（保留密钥，只更新配置）"
    fi
    system_persist_rules
    remind_security_group
}

# 旧名字，保留兼容。
system_iptables_ipsec() { system_firewall "$@"; }

system_fail2ban() {
    require_root
    ensure_cmds fail2ban-client:fail2ban sendmail:sendmail
    install_file "${MYCONF_HOME}/conf/system/jail.conf" /etc/fail2ban/jail.conf 644
    svc_enable_restart fail2ban
}

system_rclocal() {
    require_root
    # 旧版的 rc.local 写死了网卡名和规则。若它还在，给出提示（install_file 会先备份）。
    if [ -f /etc/rc.local ] && grep -qE 'iptables .*-(A|I) ' /etc/rc.local 2>/dev/null; then
        warn "/etc/rc.local 里有旧的 iptables 规则（可能写死了网卡名），将替换为不含规则的版本，旧文件会备份"
        grep -nE 'iptables' /etc/rc.local | sed 's/^/    /' >&2
    fi
    install_file "${MYCONF_HOME}/conf/system/rc-local.service" /etc/systemd/system/rc-local.service 644
    install_file "${MYCONF_HOME}/conf/system/rc.local" /etc/rc.local 755
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
        firewall | iptables-ipsec) system_firewall "$@" ;;
        fail2ban) system_fail2ban ;;
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
