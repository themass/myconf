#!/usr/bin/env bash
# strongSwan（IKEv2/IPsec）服务端。
#
# 两个版本：
#   59  strongSwan 5.9.x，ipsec.conf + stroke，推荐生产使用（配置在 strongswan_conf*/）
#   6   strongSwan 6.x，swanctl + vici，实验（配置在 strongswan_6.0_conf/）
# 动作后面带版本号，省略时用 59：  vpn.sh strongswan install 6
#
# 用法（通过 vpn.sh 调用）：
#   vpn.sh strongswan all [59|6]            一键：依赖 + 编译安装 + 配置 + 证书 + 防火墙 + 内核参数
#   vpn.sh strongswan install [59|6]        编译安装
#   vpn.sh strongswan config [59|6]         配置（默认端口 500/4500）
#   vpn.sh strongswan config-port [59|6]    配置（端口版 8081/8080）
#   vpn.sh strongswan ca [59|6]             生成 CA、服务器、客户端证书
#   vpn.sh strongswan fix [59|6]            修复连不上 / 双 charon / ipsec0 打满 CPU
#   vpn.sh strongswan check [59|6]          状态检查
#   vpn.sh strongswan clean [force]         清理残留进程、socket，重建目录和权限
#   vpn.sh strongswan status
#
# 编译参数、systemd 处理、charon-systemd 与 stroke 的互斥处理都来自线上踩过的坑，
# 这里原样保留，只改了路径、权限判断和模板渲染方式。

# shellcheck source=system.sh
source "${VPN_SHELL_DIR}/modules/system.sh"

STRONGSWAN59_VERSION="${STRONGSWAN_LEGACY_VERSION:-5.9.14}"
STRONGSWAN6_VERSION="${STRONGSWAN6_VERSION:-6.0.2}"
SS6_CONF_DIR="${MYCONF_HOME}/strongswan_6.0_conf"

strongswan_usage() {
    cat <<EOF
strongSwan 模块（版本 59 = ${STRONGSWAN59_VERSION} 的 ipsec.conf 版，6 = ${STRONGSWAN6_VERSION} 的 swanctl 版，省略时为 59）:
  all [59|6]          一键部署
  install [59|6]      编译安装
  config [59|6]       配置，默认端口 500/4500
  config-port [59|6]  配置，端口版 8081/8080
  ca [59|6]           生成证书
  fix [59|6]          修复：59 修双 charon/CA/8080 连不上；6 关闭 ipsec0 用户态 IPsec
  check [59|6]        状态检查
  clean [force]       清理残留进程和 socket；force 额外杀 ipsec 进程并清空 xfrm
  status              服务状态

环境变量: STRONGSWAN_LEGACY_VERSION（默认 ${STRONGSWAN59_VERSION}，可设 5.6.3）、STRONGSWAN6_VERSION、IPSEC_SUBNET
EOF
}

# ------------------------------------------------------------------ 共用：服务与进程

ss_disable_charon_systemd() {
    systemctl stop strongswan 2>/dev/null || true
    systemctl disable strongswan 2>/dev/null || true
    systemctl mask strongswan 2>/dev/null || true
    pkill -9 -x charon-systemd 2>/dev/null || true
}

# 6.x / --enable-systemd 装出来的 strongswan.service（charon-systemd）和 ipsec.conf/stroke 不能并存。
ss_prepare_stroke_service() {
    local unit="/etc/systemd/system/strongswan.service"
    if [ -f "$unit" ] && grep -q 'charon-systemd' "$unit" 2>/dev/null; then
        log "移除 swanctl 时代的 strongswan.service（切换到 ipsec/stroke）"
        rm -f "$unit" /etc/systemd/system/strongswan-swanctl.service
        systemctl daemon-reload
    fi
    ss_disable_charon_systemd
}

# 5.9 的 starter 读 /etc/strongswan.conf；6.x 或旧模板里的 charon.xxx= / duplicheck. 会解析失败。
ss_restore_59_main_conf() {
    local template
    if [ -f "${MYCONF_HOME}/strongswan_conf_port/strongswan.conf" ]; then
        template="${MYCONF_HOME}/strongswan_conf_port/strongswan.conf"
    else
        template="${MYCONF_HOME}/strongswan_conf/strongswan.conf"
    fi
    [ -f "$template" ] || die "缺少 5.9 的 strongswan.conf 模板: ${MYCONF_HOME}/strongswan_conf*/"
    install_file "$template" /etc/strongswan.conf 644
    rm -f /etc/strongswan.d/charon/zz-no-kernel-libipsec.conf 2>/dev/null || true
    if [ -f "${MYCONF_HOME}/strongswan_conf_port/charon.conf" ]; then
        install_file "${MYCONF_HOME}/strongswan_conf_port/charon.conf" /etc/strongswan.d/charon.conf 644
    fi
}

ss_ensure_stroke_charon_only() {
    log "确保只有 stroke 的 charon 处理 UDP（避免 charon-systemd 抢 8080/8081）"
    ss_disable_charon_systemd
    systemctl stop strongswan-starter 2>/dev/null || true
    pkill -9 -f '/usr/libexec/ipsec/charon' 2>/dev/null || true
    pkill -9 -f '/usr/lib/ipsec/charon' 2>/dev/null || true
    sleep 1
    systemctl enable strongswan-starter 2>/dev/null || true
    systemctl start strongswan-starter 2>/dev/null || ipsec restart
    sleep 1
    echo "--- 8080/8081 必须是 stroke 的 charon，不能是 charon-systemd ---"
    ss -ulnp 2>/dev/null | grep -E ':8080|:8081' || true
    ps aux 2>/dev/null | grep '[c]haron' || true
    if ss -ulnp 2>/dev/null | grep -E ':8080' | grep -q charon-sy; then
        err "UDP 8080 仍被 charon-systemd 占用。执行: systemctl mask strongswan && pkill -9 charon-systemd && ipsec restart"
        return 1
    fi
}

ss_ensure_ca_in_cacerts() {
    [ -f /etc/ipsec.d/cacerts/caCert.pem ] && return 0
    local ca_dir="${TMP_HOME}/ca"
    if [ -f "${ca_dir}/caCert.pem" ]; then
        log "从 ${ca_dir}/caCert.pem 补装 CA 到 /etc/ipsec.d/cacerts/"
        mkdir -p /etc/ipsec.d/cacerts
        cp "${ca_dir}/caCert.pem" /etc/ipsec.d/cacerts/
        return 0
    fi
    err "缺少 /etc/ipsec.d/cacerts/caCert.pem，请运行: vpn.sh strongswan ca"
    return 1
}

ss_start_service() {
    systemctl daemon-reload 2>/dev/null || true
    ss_disable_charon_systemd
    # 5.9.x stroke 优先用 starter，避免和 charon-systemd 双进程抢端口。
    if systemctl list-unit-files 2>/dev/null | grep -q '^strongswan-starter\.service'; then
        systemctl enable strongswan-starter
        systemctl restart strongswan-starter
        return
    fi
    if systemctl list-unit-files 2>/dev/null | grep -q '^strongswan\.service'; then
        if [ -f /etc/systemd/system/strongswan.service ] && grep -q 'charon-systemd' /etc/systemd/system/strongswan.service 2>/dev/null; then
            err "strongswan.service 仍是 swanctl/charon-systemd，请重新运行 5.9 的安装"
        else
            systemctl enable strongswan
            systemctl restart strongswan
            return
        fi
    fi
    if systemctl list-unit-files 2>/dev/null | grep -q '^ipsec\.service'; then
        systemctl enable ipsec
        systemctl restart ipsec
        return
    fi
    if have ipsec; then
        ipsec restart
        return
    fi
    err "strongSwan 已安装，但没有找到服务单元"
}

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
    local charon_bin unit_type=simple
    # 不复用上游的 unit：它的 ExecStartPost 会在证书就位前执行 swanctl。
    charon_bin="$(ss_resolve_charon_bin)" || {
        err "安装后没有找到 charon / charon-systemd"
        return 1
    }
    case "$charon_bin" in
        *charon-systemd) unit_type=notify ;;
    esac
    install_template "${TEMPLATE_DIR}/strongswan/strongswan.service" /etc/systemd/system/strongswan.service 644 \
        "UNIT_TYPE=${unit_type}" "CHARON_BIN=${charon_bin}"
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

ss_install_59() {
    log "编译安装 strongSwan ${STRONGSWAN59_VERSION}（ipsec.conf / stroke）"
    ss_fetch_source "$STRONGSWAN59_VERSION"
    ./configure --prefix=/usr --sysconfdir=/etc --enable-openssl --enable-nat-transport --disable-mysql \
        --disable-ldap --disable-static --enable-shared --enable-md4 --enable-eap-mschapv2 --enable-eap-aka \
        --enable-eap-aka-3gpp2 --enable-eap-gtc --enable-eap-identity --enable-eap-md5 --enable-eap-peap \
        --enable-eap-radius --enable-eap-sim --enable-eap-sim-file --enable-eap-simaka-pseudonym \
        --enable-eap-simaka-reauth --enable-eap-simaka-sql --enable-eap-tls --enable-eap-tnc --enable-eap-ttls \
        --enable-systemd --disable-kernel-libipsec || die "configure 失败"
    make -j"$(nproc 2>/dev/null || echo 1)" || die "编译失败"
    make install || die "make install 失败"
    ldconfig 2>/dev/null || true
    ss_purge_libipsec_plugin || true
    ss_prepare_stroke_service
    ss_restore_59_main_conf || die "写入 strongswan.conf 失败"
    ss_start_service
    ipsec version 2>/dev/null || true
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

# 5.9：默认端口。
ss_config_59() {
    local dir="${MYCONF_HOME}/strongswan_conf"
    install_file "${dir}/ipsec.conf" /etc/ipsec.conf 644
    install_file "${dir}/charon.conf" /etc/strongswan.d/charon.conf 644
    install_file "${dir}/ipsec.secrets" /etc/ipsec.secrets 600
    install_file "${dir}/strongswan.conf" /etc/strongswan.conf 644
    ipsec restart
}

# 5.9：端口版 8081/8080 + RADIUS。
ss_config_port_59() {
    local dir="${MYCONF_HOME}/strongswan_conf_port"
    ss_ensure_stroke_charon_only || true
    ss_ensure_ca_in_cacerts || true
    install_file "${dir}/ipsec.conf" /etc/ipsec.conf 644
    install_file "${dir}/charon.conf" /etc/strongswan.d/charon.conf 644
    install_file "${dir}/ipsec.secrets" /etc/ipsec.secrets 600
    install_file "${dir}/strongswan.conf" /etc/strongswan.conf 644

    [ -f /etc/ipsec.d/cacerts/caCert.pem ] || warn "缺少 CA: /etc/ipsec.d/cacerts/caCert.pem，请运行: vpn.sh strongswan ca"
    if ! grep -q 'leftikeport=8080' /etc/ipsec.conf || ! grep -q 'radius-natt' /etc/ipsec.conf; then
        warn "/etc/ipsec.conf 缺少 radius-natt/8080，更新仓库后重新运行 config-port"
    fi
    ipsec restart
    echo "--- ipsec listall (radius) ---"
    ipsec listall 2>/dev/null | grep -E 'radius-natt|radius:' || true
}

# 6：把 swanctl 模板的 {{SERVER_IP}} 换成本机公网地址。template 是模板文件名。
ss_config_6_with() {
    local template="$1" server_ip
    server_ip="$(detect_server_address)" || die "无法获取服务器公网 IP，请设置 SERVER_ADDRESS"
    log "服务器 IP: ${server_ip}"
    ss_install_systemd_unit || return 1
    ss_install_charon_dropins || return 1
    install_file "${SS6_CONF_DIR}/strongswan.conf" /etc/strongswan.conf 644
    mkdir -p /etc/swanctl/{private,x509,x509ca,scripts}
    install_template "${SS6_CONF_DIR}/${template}" /etc/swanctl/swanctl.conf 600 "SERVER_IP=${server_ip}"
    install_template "${SS6_CONF_DIR}/${template}" /etc/swanctl.conf 600 "SERVER_IP=${server_ip}"
    if [ -f /etc/swanctl/x509ca/caCert.pem ]; then
        ss_reload_6 || return 1
        swanctl --list-conns
    else
        warn "尚未生成证书，跳过启动。接着运行: vpn.sh strongswan ca 6"
    fi
}

ss_config_6() { ss_config_6_with swanctl.conf.template; }
ss_config_port_6() { ss_config_6_with swanctl_port.conf.template; }

# ------------------------------------------------------------------ 证书

# 5.9：证书写进 /etc/ipsec.d，CN 和 SAN 是本机公网地址。
ss_ca_59() {
    local ip dir
    ip="$(detect_server_address)" || die "无法获取服务器公网 IP，请设置 SERVER_ADDRESS"
    dir="${TMP_HOME}/ca"
    mkdir -p "$dir" /etc/ipsec.d/cacerts /etc/ipsec.d/certs /etc/ipsec.d/private
    cd "$dir" || die "进入 ${dir} 失败"
    log "生成证书，CN=${ip}"
    ipsec pki --gen --outform pem >caKey.pem
    ipsec pki --self --in caKey.pem --dn "C=CN, O=timeline, CN=${ip}" --ca --outform pem >caCert.pem
    ipsec pki --gen --outform pem >serverKey.pem
    ipsec pki --pub --in serverKey.pem | ipsec pki --issue --cacert caCert.pem --cakey caKey.pem \
        --dn "C=CN, O=timeline, CN=${ip}" --san="$ip" --flag serverAuth --flag ikeIntermediate --outform pem >serverCert.pem
    ipsec pki --gen --outform pem >clientKey.pem
    ipsec pki --pub --in clientKey.pem | ipsec pki --issue --cacert caCert.pem --cakey caKey.pem \
        --dn "C=CN, O=timeline, CN=client" --outform pem >clientCert.pem
    openssl pkcs12 -export -inkey clientKey.pem -in clientCert.pem -name "client" -certfile caCert.pem \
        -caname "$ip" -out clientCert.p12 -passout pass:

    cp caCert.pem /etc/ipsec.d/cacerts/
    cp serverCert.pem /etc/ipsec.d/certs/
    cp serverKey.pem /etc/ipsec.d/private/
    cp clientCert.pem /etc/ipsec.d/certs/
    cp clientKey.pem /etc/ipsec.d/private/
    chmod 600 /etc/ipsec.d/private/*.pem
    ipsec restart
    log "客户端 PKCS#12（无密码）: ${dir}/clientCert.p12"
}

# 6：证书写进 /etc/swanctl。
ss_ca_6() {
    local ip dir
    ip="$(detect_server_address)" || die "无法获取服务器公网 IP，请设置 SERVER_ADDRESS"
    dir="${TMP_HOME}/ca6"
    mkdir -p "$dir" /etc/swanctl/{x509,private,x509ca}
    cd "$dir" || die "进入 ${dir} 失败"
    [ -f /etc/strongswan.conf ] || install_file "${SS6_CONF_DIR}/strongswan.conf" /etc/strongswan.conf 644

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

ss_fix_59() {
    ss_ensure_stroke_charon_only
    ss_ensure_ca_in_cacerts || true
    if [ -f "${MYCONF_HOME}/strongswan_conf_port/ipsec.conf" ]; then
        install_file "${MYCONF_HOME}/strongswan_conf_port/ipsec.conf" /etc/ipsec.conf 644
    fi
    ipsec restart
    ipsec listall 2>/dev/null | grep -E 'radius-natt|radius:' || true
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
    log "清理完成。重新启动: systemctl start strongswan（6）或 ipsec restart（59）"
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

ss_check_59() {
    echo "=== strongSwan 5.9 状态 ==="
    ipsec version 2>/dev/null || true
    ipsec statusall 2>/dev/null | head -n 30 || ipsec status 2>/dev/null || true
    iptables -L -n | head -n 30
    ps aux | grep '[c]haron' || echo "没有 charon 进程"
}

# ------------------------------------------------------------------ 一键

ss_all_59() {
    log "strongSwan ${STRONGSWAN59_VERSION} 一键部署（端口版 8081/8080 + RADIUS）"
    system_init
    ss_install_59
    ss_config_port_59
    ss_ca_59
    system_net
    system_iptables_ipsec
    ss_check_59
    log "部署完成（IKE UDP 8081 / NAT-T 8080）"
}

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

# 带版本号的动作分发：version 为 59 或 6（默认 59）。
ss_versioned() {
    local fn="$1" version="${2:-59}"
    case "$version" in
        59 | 6) "ss_${fn}_${version}" ;;
        *) die "版本只能是 59 或 6: ${version}" ;;
    esac
}

strongswan_main() {
    local action="${1:-}"
    [ $# -gt 0 ] && shift
    case "$action" in
        all | install | config | config-port | ca | fix | clean)
            require_root
            ;;
    esac
    case "$action" in
        all) ss_versioned all "$@" ;;
        install) ss_versioned install "$@" ;;
        config) ss_versioned config "$@" ;;
        config-port) ss_versioned config_port "$@" ;;
        ca) ss_versioned ca "$@" ;;
        fix) ss_versioned fix "$@" ;;
        check) ss_versioned check "$@" ;;
        clean) ss_clean "$@" ;;
        status)
            ipsec statusall 2>/dev/null || systemctl status strongswan --no-pager -l
            ;;
        '' | help | -h | --help) strongswan_usage ;;
        *)
            err "未知动作: ${action}"
            strongswan_usage
            return 2
            ;;
    esac
}
