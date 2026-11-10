#!/usr/bin/env bash
# strongSwan 6.x（IKEv2/IPsec，swanctl + vici）服务端。
#
# 用法（通过 vpn.sh 调用）：
#   vpn.sh strongswan all                   一键：编译安装 + 配置 + 证书 + 防火墙 + 内核参数
#   vpn.sh strongswan install               编译安装 strongSwan 6.x
#   vpn.sh strongswan config                配置（IKE 8081 / NAT-T 8080，可用 SS_IKE_PORT / SS_NATT_PORT 改）
#   vpn.sh strongswan config-port           同 config（保留旧名字）
#   vpn.sh strongswan ca                    生成 CA、服务器、客户端证书
#   vpn.sh strongswan fix                   关闭 ipsec0 用户态 IPsec，修复 CPU 打满
#   vpn.sh strongswan check                 状态检查
#   vpn.sh strongswan clean [force]         清理残留进程、socket，重建目录和权限
#   vpn.sh strongswan status
#
# 只支持 6.x。5.9（ipsec.conf / stroke）的代码和配置已经删除。

# shellcheck source=system.sh
source "${VPN_SHELL_DIR}/modules/system.sh"

STRONGSWAN6_VERSION="${STRONGSWAN6_VERSION:-6.0.2}"
SS6_CONF_DIR="${MYCONF_HOME}/conf/strongswan/6"
# IKE / NAT-T 端口。默认 8081 / 8080，和现有线上节点、后端 host_v2.port=8080 一致。
SS_IKE_PORT="${SS_IKE_PORT:-8081}"
SS_NATT_PORT="${SS_NATT_PORT:-8080}"

strongswan_usage() {
    cat <<USAGE
strongSwan 模块（6.x，版本 ${STRONGSWAN6_VERSION}，swanctl + vici）:
  all             一键部署（编译 + 配置 + 证书 + 防火墙 + 内核参数）
  install         编译安装
  config          配置：IKE ${SS_IKE_PORT}/udp，NAT-T ${SS_NATT_PORT}/udp，地址池 ${IPSEC_SUBNET}
  config-port     同 config（保留旧名字）
  ca              生成证书
  fix             关闭 ipsec0 用户态 IPsec（kernel-libipsec），修复 CPU 打满
  check           状态检查
  clean [force]   清理残留进程和 socket；force 额外杀 ipsec 进程并清空 xfrm
  status          服务状态

环境变量: STRONGSWAN6_VERSION（默认 ${STRONGSWAN6_VERSION}）、SS_IKE_PORT（${SS_IKE_PORT}）、SS_NATT_PORT（${SS_NATT_PORT}）、
          IPSEC_SUBNET（${IPSEC_SUBNET}）、IPSEC_SUBNET6（${IPSEC_SUBNET6}）、SERVER_ADDRESS（默认自动识别）
USAGE
}

# ------------------------------------------------------------------ 共用：服务与进程







ss_resolve_charon_bin() {
    local c
    for c in /usr/lib/ipsec/charon-systemd /usr/sbin/charon-systemd /usr/libexec/ipsec/charon-systemd \
        /usr/lib/ipsec/charon /usr/libexec/ipsec/charon; do
        if [ -x "$c" ]; then
            printf '%s\n' "$c"
            return 0
        fi
    done
    return 1
}

ss_install_systemd_unit() {
    local charon_bin swanctl_bin unit_type=simple
    # 用自己的 unit，不用上游的 strongswan-swanctl.service。启动后由 ExecStartPost 加载 swanctl.conf
    # （charon 自己不读它），加载失败不影响服务启动：首次安装时证书还没生成，之后 ss_reload_6 会再加载。
    charon_bin="$(ss_resolve_charon_bin)" || {
        err "安装后没有找到 charon / charon-systemd"
        return 1
    }
    swanctl_bin="$(command -v swanctl)" || {
        err "安装后没有找到 swanctl"
        return 1
    }
    case "$charon_bin" in
        *charon-systemd) unit_type=notify ;;
    esac
    install_template "${TEMPLATE_DIR}/strongswan/strongswan.service" /etc/systemd/system/strongswan.service 644 \
        "UNIT_TYPE=${unit_type}" "CHARON_BIN=${charon_bin}" "SWANCTL_BIN=${swanctl_bin}"
    rm -f /etc/systemd/system/strongswan-swanctl.service
    systemctl daemon-reload
}

# kernel-libipsec 是用户态 IPsec：开了就走 ipsec0 隧道，客户端一连 CPU 就被打满。必须只用内核 XFRM。
ss_purge_libipsec_plugin() {
    local pattern f
    for pattern in '/usr/lib/ipsec/plugins/libstrongswan-kernel-libipsec.so*' \
        '/usr/libexec/ipsec/plugins/libstrongswan-kernel-libipsec.so*'; do
        for f in $pattern; do
            [ -e "$f" ] || continue
            rm -f "$f"
            log "已移除用户态 IPsec 插件: ${f}"
        done
    done
    if [ -f /etc/strongswan.d/charon/kernel-libipsec.conf ]; then
        # 用 awk 重写，不依赖 sed -i。
        awk '{ sub(/load *= *yes/, "load = no"); print }' /etc/strongswan.d/charon/kernel-libipsec.conf \
            >/etc/strongswan.d/charon/kernel-libipsec.conf.new \
            && mv -f /etc/strongswan.d/charon/kernel-libipsec.conf.new /etc/strongswan.d/charon/kernel-libipsec.conf
    fi
}

ss_install_charon_dropins() {
    local src="${SS6_CONF_DIR}/charon/zz-no-kernel-libipsec.conf"
    [ -f "$src" ] || {
        err "缺少 ${src}"
        return 1
    }
    mkdir -p /etc/strongswan.d/charon
    install_file "$src" /etc/strongswan.d/charon/zz-no-kernel-libipsec.conf 644
    ss_purge_libipsec_plugin || true
}

# ------------------------------------------------------------------ 编译安装

# 下载并解压源码包到 ${TMP_HOME}，进入源码目录。
ss_fetch_source() {
    local version="$1" tarball="strongswan-${1}.tar.bz2"
    mkdir -p "$TMP_HOME"
    cd "$TMP_HOME" || die "进入 ${TMP_HOME} 失败"
    if [ ! -f "$tarball" ]; then
        download "https://download.strongswan.org/${tarball}" "$tarball" || die "下载 ${tarball} 失败"
    fi
    [ -d "strongswan-${version}" ] || tar -jxf "$tarball" || die "解压 ${tarball} 失败"
    cd "strongswan-${version}" || die "进入源码目录失败"
}


ss_install_6() {
    log "编译安装 strongSwan ${STRONGSWAN6_VERSION}（swanctl）"
    ss_fetch_source "$STRONGSWAN6_VERSION"
    # 只用内核 XFRM (kernel-netlink)。不要开 kernel-libipsec，否则走 ipsec0 用户态隧道，客户端一连就打满 CPU。
    ./configure --prefix=/usr --sysconfdir=/etc --enable-openssl --enable-nat-transport --enable-eap-radius \
        --enable-eap-identity --enable-eap-md5 --enable-eap-mschapv2 --enable-eap-tls --enable-eap-ttls \
        --enable-vici --enable-swanctl --enable-systemd --enable-kernel-netlink --disable-kernel-libipsec \
        || die "configure 失败"
    make -j"$(nproc 2>/dev/null || echo 1)" || die "编译失败"
    make install || die "make install 失败"
    ss_purge_libipsec_plugin || true
    ss_install_charon_dropins || die "写入 charon drop-in 失败"

    groupadd -r strongswan 2>/dev/null || true
    useradd -r -g strongswan -s /bin/false -d /var/lib/strongswan strongswan 2>/dev/null || true
    mkdir -p /etc/swanctl/{private,x509,x509ca,scripts} /var/log/strongswan /var/lib/strongswan /var/run/charon
    chown -R strongswan:strongswan /etc/swanctl /var/log/strongswan /var/lib/strongswan 2>/dev/null || true

    ss_install_systemd_unit || die "安装 systemd 服务失败"
    chmod 755 /var/log/strongswan /etc/swanctl /var/run/charon
    chmod 700 /etc/swanctl/private 2>/dev/null || true

    ln -sf /usr/lib/ipsec/libstrongswan.so.0 /usr/lib/libstrongswan.so.0 2>/dev/null || true
    ln -sf /usr/lib/ipsec/libcharon.so.0 /usr/lib/libcharon.so.0 2>/dev/null || true
    ldconfig
    systemctl enable strongswan
    log "strongSwan ${STRONGSWAN6_VERSION} 已安装；配置和证书就绪后运行: vpn.sh strongswan ca 6"
}

# ------------------------------------------------------------------ 配置



# 6：把 swanctl 模板的 {{SERVER_IP}} 换成本机公网地址。template 是模板文件名。
# 渲染 /etc/strongswan.conf（IKE / NAT-T 端口）。端口不合法直接报错，不写半成品。
ss_render_main_conf() {
    case "$SS_IKE_PORT$SS_NATT_PORT" in *[!0-9]*) die "SS_IKE_PORT / SS_NATT_PORT 必须是数字" ;; esac
    [ "$SS_IKE_PORT" != "$SS_NATT_PORT" ] || die "SS_IKE_PORT 和 SS_NATT_PORT 不能相同"
    install_template "${SS6_CONF_DIR}/strongswan.conf" /etc/strongswan.conf 644 \
        "IKE_PORT=${SS_IKE_PORT}" "NATT_PORT=${SS_NATT_PORT}"
}

ss_config_6_with() {
    local template="$1" server_ip
    server_ip="$(detect_server_address)" || die "无法获取服务器公网 IP，请设置 SERVER_ADDRESS"
    log "服务器 IP: ${server_ip}"
    ss_install_systemd_unit || return 1
    ss_install_charon_dropins || return 1
    ss_render_main_conf
    mkdir -p /etc/swanctl/{private,x509,x509ca,scripts}
    log "地址池: ${IPSEC_SUBNET}, ${IPSEC_SUBNET6}；IKE ${SS_IKE_PORT}/udp，NAT-T ${SS_NATT_PORT}/udp"
    install_template "${SS6_CONF_DIR}/${template}" /etc/swanctl/swanctl.conf 600 \
        "SERVER_IP=${server_ip}" "POOL4=${IPSEC_SUBNET}" "POOL6=${IPSEC_SUBNET6}"
    install_template "${SS6_CONF_DIR}/${template}" /etc/swanctl.conf 600 \
        "SERVER_IP=${server_ip}" "POOL4=${IPSEC_SUBNET}" "POOL6=${IPSEC_SUBNET6}"
    if [ -f /etc/swanctl/x509ca/caCert.pem ]; then
        ss_reload_6 || return 1
        swanctl --list-conns
    else
        warn "尚未生成证书，跳过启动。接着运行: vpn.sh strongswan ca 6"
    fi
}

ss_config_6() { ss_config_6_with swanctl.conf.template; }
# 端口版：和 config 用同一个模板，端口由 SS_IKE_PORT / SS_NATT_PORT 决定（默认就是 8081/8080）。
ss_config_port_6() { ss_config_6_with swanctl.conf.template; }

# ------------------------------------------------------------------ 证书


# 6：证书写进 /etc/swanctl。
ss_ca_6() {
    local ip dir
    ip="$(detect_server_address)" || die "无法获取服务器公网 IP，请设置 SERVER_ADDRESS"
    dir="${TMP_HOME}/ca6"
    mkdir -p "$dir" /etc/swanctl/{x509,private,x509ca}
    cd "$dir" || die "进入 ${dir} 失败"
    [ -f /etc/strongswan.conf ] || ss_render_main_conf

    log "生成证书，CN=${ip}"
    pki --gen --outform pem >caKey.pem
    pki --self --in caKey.pem --dn "C=CN, O=timeline, CN=${ip}" --ca --outform pem >caCert.pem
    pki --gen --outform pem >serverKey.pem
    pki --pub --in serverKey.pem | pki --issue --cacert caCert.pem --cakey caKey.pem \
        --dn "C=CN, O=timeline, CN=${ip}" --san="$ip" --flag serverAuth --flag ikeIntermediate --outform pem >serverCert.pem
    pki --gen --outform pem >clientKey.pem
    pki --pub --in clientKey.pem | pki --issue --cacert caCert.pem --cakey caKey.pem \
        --dn "C=CN, O=timeline, CN=client" --outform pem >clientCert.pem
    openssl pkcs12 -export -inkey clientKey.pem -in clientCert.pem -name "client" -certfile caCert.pem \
        -caname "$ip" -out clientCert.p12 -passout pass:

    cp serverCert.pem /etc/swanctl/x509/
    cp serverKey.pem /etc/swanctl/private/serverCert.pem
    cp clientCert.pem /etc/swanctl/x509/
    cp clientKey.pem /etc/swanctl/private/clientCert.pem
    # 不要把 .p12 放进 x509/：charon 会当 PEM 解析，报 OpenSSL X.509 parsing failed。
    cp caCert.pem /etc/swanctl/x509ca/
    chown -R strongswan:strongswan /etc/swanctl
    chmod 644 /etc/swanctl/x509/*.pem /etc/swanctl/x509ca/*.pem
    chmod 600 /etc/swanctl/private/*.pem

    ss_reload_6 || return 1
    swanctl --list-certs
    log "客户端 PKCS#12（无密码）: ${dir}/clientCert.p12"
}

# ------------------------------------------------------------------ 6 的加载与校验

ss_verify_6() {
    local logf=/var/log/charon.log
    if ip link show ipsec0 >/dev/null 2>&1; then
        err "仍存在 ipsec0 设备：用户态 IPsec 未关闭，客户端流量会把 CPU 打满。执行: vpn.sh strongswan fix 6"
        return 1
    fi
    if [ -f "$logf" ] && tail -30 "$logf" | grep -q 'created TUN device: ipsec0'; then
        err "charon 最近仍创建了 ipsec0，重新编译并执行 vpn.sh strongswan fix 6"
        return 1
    fi
    log "OK: 未检测到 ipsec0（走内核 XFRM）"
}

ss_reload_6() {
    [ -f /etc/swanctl/x509ca/caCert.pem ] || {
        err "缺少 CA 证书，请先运行: vpn.sh strongswan ca 6"
        return 1
    }
    if [ ! -f /etc/swanctl/x509/serverCert.pem ] || [ ! -f /etc/swanctl/private/serverCert.pem ]; then
        err "缺少服务器证书或私钥，请先运行: vpn.sh strongswan ca 6"
        return 1
    fi
    systemctl enable strongswan 2>/dev/null || true
    systemctl restart strongswan || return 1
    sleep 2
    if ! swanctl --load-all --noprompt; then
        err "swanctl --load-all 失败。常见原因：swanctl.conf 语法错误、证书缺失、x509/ 下有 .p12 文件"
        return 1
    fi
    ss_verify_6
}

ss_fix_6() {
    log "关闭 userspace IPsec (kernel-libipsec)"
    ss_install_charon_dropins || return 1
    if [ -f /etc/strongswan.conf ] && ! grep -q 'kernel-libipsec' /etc/strongswan.conf; then
        warn "/etc/strongswan.conf 里没有 kernel-libipsec load = no，运行: vpn.sh strongswan config 6"
    fi
    ss_reload_6
}


# ------------------------------------------------------------------ 清理与检查

ss_prepare_dirs() {
    mkdir -p /var/run/charon /var/log/strongswan /etc/swanctl/{private,x509,x509ca,scripts}
    chown -R strongswan:strongswan /var/run/charon /var/log/strongswan /etc/swanctl 2>/dev/null || true
    chmod 755 /var/run/charon /var/log/strongswan /etc/swanctl
    chmod 700 /etc/swanctl/private 2>/dev/null || true
}

ss_clean() {
    local mode="${1:-}"
    log "停止服务"
    systemctl stop strongswan 2>/dev/null || true
    systemctl stop strongswan-swanctl 2>/dev/null || true
    if [ "$mode" = "force" ]; then
        systemctl stop ipsec 2>/dev/null || true
        pkill -9 -f charon 2>/dev/null || true
        pkill -9 -f strongswan 2>/dev/null || true
        pkill -9 -f ipsec 2>/dev/null || true
        sleep 5
        pgrep -f charon >/dev/null && pkill -9 -f charon
        rm -f /var/run/strongswan* /var/lock/strongswan* /tmp/strongswan* 2>/dev/null || true
        # 清空内核里残留的 IPsec 状态，否则新连接可能被旧策略吃掉。
        ip xfrm state flush 2>/dev/null || true
        ip xfrm policy flush 2>/dev/null || true
    else
        pkill -f charon 2>/dev/null || true
        sleep 2
    fi
    rm -f /var/run/charon.vici /var/run/charon.pid 2>/dev/null || true
    rm -f /var/run/charon/* 2>/dev/null || true
    ss_prepare_dirs
    systemctl daemon-reload
    log "清理完成。重新启动: systemctl start strongswan"
}

ss_check_6() {
    echo "=== strongSwan 6 状态 ==="
    systemctl status strongswan --no-pager -l || true
    swanctl --list-conns || true
    swanctl --list-certs || true
    echo "--- 目录与 socket ---"
    ls -la /var/run/charon/ /var/log/strongswan/ /etc/swanctl/ /var/run/charon.vici 2>&1 | head -n 30
    echo "--- 进程 ---"
    ps aux | grep '[c]haron' || echo "没有 charon 进程"
    echo "--- 最近日志 ---"
    journalctl -u strongswan -n 20 --no-pager 2>/dev/null || true
    ss_verify_6 || true
}


# ------------------------------------------------------------------ 一键


ss_all_6() {
    log "strongSwan ${STRONGSWAN6_VERSION} 一键部署"
    system_init
    ss_install_6
    ss_config_6
    ss_ca_6
    system_net
    system_iptables_ipsec
    ss_check_6
    log "部署完成"
}


strongswan_main() {
    local action="${1:-}"
    [ $# -gt 0 ] && shift
    # 兼容旧命令 "strongswan all 6"：末尾的 6 直接忽略，其它版本号报错。
    case "${1:-}" in
        '') ;;
        6) shift ;;
        *) die "只支持 strongSwan 6.x（不再支持 5.9）: $1" ;;
    esac
    case "$action" in
        all | install | config | config-port | ca | fix | clean)
            require_root
            ;;
    esac
    case "$action" in
        all) ss_all_6 "$@" ;;
        install) ss_install_6 "$@" ;;
        config) ss_config_6 "$@" ;;
        config-port) ss_config_port_6 "$@" ;;
        ca) ss_ca_6 "$@" ;;
        fix) ss_fix_6 "$@" ;;
        check) ss_check_6 "$@" ;;
        clean) ss_clean "$@" ;;
        status)
            ipsec statusall 2>/dev/null || swanctl --stats 2>/dev/null || systemctl status strongswan --no-pager -l
            ;;
        '' | help | -h | --help) strongswan_usage ;;
        *)
            err "未知动作: ${action}"
            strongswan_usage
            return 2
            ;;
    esac
}
