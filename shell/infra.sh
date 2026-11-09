#!/usr/bin/env bash
# 非 VPN 的服务器软件安装：nginx(OpenResty)、Redis、MySQL、FreeRADIUS、JDK/Maven。
# 取代旧的 soft_setup.sh / soft_setup_web.sh / setup.sh。启停和状态见 svc.sh。
#
#   bash infra.sh nginx | redis | mysql | radius | jdk | all
#   bash infra.sh help
#
# 配置里的 innerip 占位符会自动换成本机内网地址（不用再手改网卡/IP）；
# 没有内网地址时只绑 127.0.0.1，需要对内网其它机器开放时设置 INFRA_BIND=<地址>。
# 所有动作可重复运行；已有配置变化时先备份再覆盖；数据目录里已有数据不会被删除或重新初始化。

if [ -z "${BASH_VERSION:-}" ]; then
    command -v bash >/dev/null 2>&1 && exec bash "$0" "$@"
    echo "需要 bash: bash $0 ..." >&2
    exit 2
fi

VPN_SHELL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export VPN_SHELL_DIR
# shellcheck source=lib/common.sh
source "${VPN_SHELL_DIR}/lib/common.sh"

INFRA_OPT="${INFRA_OPT:-/opt}"
MYSQL_VERSION="${MYSQL_VERSION:-5.6.40}"
MYSQL_DATADIR="${MYSQL_DATADIR:-/home/mysql/db_data}"
INFRA_JDK_PKG="${INFRA_JDK_PKG:-openjdk-17-jdk-headless}"
OPENRESTY_PREFIX="/usr/local/openresty"

infra_usage() {
    cat <<EOF
用法: bash infra.sh <软件>

  nginx    OpenResty（官方 apt 源，最新版，不用编译）+ conf/nginx 里的站点配置
  redis    Redis（apt），配置取自 conf/redis/redis.conf
  mysql    MySQL ${MYSQL_VERSION}（官方 tarball + systemd），配置取自 conf/mysql/my.cnf
  radius   FreeRADIUS 3.2.x（NetworkRadius 官方 apt 源）；sql 模块取自 conf/radius/sql.conf，clients.conf 日常用 radius.sh 更新
  jdk      ${INFRA_JDK_PKG} + maven（apt）
  php      PHP ${PHP_VERSION:-8.4}（sury 源）：php-fpm、常用扩展、composer；池 web 用 unix socket
  postgres PostgreSQL ${PG_VERSION:-17}（PGDG 源）：只听内网地址，pg_hba 只放内网段和本机，全部 scram-sha-256
  all      依次安装 mysql radius nginx redis jdk php postgres
  help     本说明

环境变量:
  INFRA_BIND            服务绑定的地址（默认自动识别内网地址，没有就 127.0.0.1）
  INFRA_REDIS_PASSWORD  覆盖 redis.conf 里的 requirepass
  INFRA_MYSQL_PUBLIC=1  MySQL 绑定 0.0.0.0（默认只绑 INFRA_BIND；root 初始无密码，别轻易公开）
  MYSQL_VERSION / INFRA_JDK_PKG / MYSQL_DATADIR / PHP_VERSION（默认 8.4）/ PG_VERSION（默认 17）/ PG_PORT / PG_ADMIN_PASSWORD（只读环境变量，不落盘）

启停、状态、检查: bash svc.sh help
EOF
}

# ------------------------------------------------------------------ 小工具

# 新机器上 unattended-upgrades 常常占着 dpkg 锁；让 apt 自己等（最长 5 分钟），不要杀它、也不要直接报错。
infra_apt_install() {
    DEBIAN_FRONTEND=noninteractive apt-get -o DPkg::Lock::Timeout=300 install -y "$@"
}

infra_need_apt() {
    have apt-get || die "只支持 apt 系统（Debian / Ubuntu）"
    apt_update_once || die "apt-get update 失败"
}

# 本机内网地址；INFRA_BIND 优先。结果缓存，只提示一次。
infra_ip() {
    if [ -z "${_INFRA_IP:-}" ]; then
        if [ -n "${INFRA_BIND:-}" ]; then
            _INFRA_IP="$INFRA_BIND"
        else
            _INFRA_IP="$(ip -4 -o addr show scope global 2>/dev/null | awk '{print $4}' | cut -d/ -f1 \
                | grep -E '^(10\.|192\.168\.|172\.(1[6-9]|2[0-9]|3[01])\.)' | head -n 1)"
            if [ -z "$_INFRA_IP" ]; then
                warn "没有找到内网地址，服务只绑定 127.0.0.1（需要对外/内网开放请设置 INFRA_BIND=<地址>）"
                _INFRA_IP="127.0.0.1"
            fi
        fi
    fi
    printf '%s\n' "$_INFRA_IP"
}

# infra_put <源文件> <目标> <权限> [sed 表达式...]
# 把 innerip 换成本机地址，再套用额外的 sed 表达式，最后走 install_file（内容变了才备份）。
infra_put() {
    local src="$1" dst="$2" mode="$3" tmp e
    local args=()
    shift 3
    [ -f "$src" ] || die "缺少文件: $src"
    args=(-e "s/innerip/$(infra_ip)/g")
    for e in "$@"; do
        args+=(-e "$e")
    done
    tmp="$(mktemp "${TMPDIR:-/tmp}/infra.XXXXXX")" || die "无法创建临时文件"
    sed "${args[@]}" "$src" >"$tmp"
    install_file "$tmp" "$dst" "$mode"
    rm -f "$tmp"
}

# ------------------------------------------------------------------ nginx (OpenResty)

# 旧脚本用源码编译 nginx 1.24 + 8 个第三方模块。改用 OpenResty 官方 apt 源：
# 内核和模块（echo / srcache / set-misc / redis2 / NDK / headers-more / lua 等）由官方打包，
# 随 apt 升级。cache_purge、consistent_hash、php_session、slowfs_cache 官方包没有，
# 配置里也没有用到它们的指令（只用了 stub_status）；一致性哈希可用内置的 `hash $key consistent;`。
infra_nginx() {
    require_root
    infra_need_apt
    [ "$(detect_arch)" = "amd64" ] || die "OpenResty 官方 apt 源这里只验证过 amd64"
    # shellcheck disable=SC1091
    . /etc/os-release
    case "${ID:-}" in ubuntu | debian) ;; *) die "只支持 Ubuntu / Debian，当前: ${ID:-unknown}" ;; esac
    ensure_cmds gpg:gnupg curl

    if systemctl is-active --quiet nginx 2>/dev/null; then
        warn "发行版自带的 nginx 正在运行，停掉并禁用，改用 OpenResty"
        systemctl disable --now nginx >/dev/null 2>&1 || true
    fi

    local key
    key="$(mktemp "${TMPDIR:-/tmp}/openresty-key.XXXXXX")" || die "无法创建临时文件"
    download "https://openresty.org/package/pubkey.gpg" "$key" || die "下载 OpenResty 签名密钥失败"
    gpg --batch --yes --dearmor -o /usr/share/keyrings/openresty.gpg "$key" || die "导入签名密钥失败"
    rm -f "$key"
    printf 'deb [signed-by=/usr/share/keyrings/openresty.gpg] https://openresty.org/package/%s %s main\n' \
        "$ID" "${VERSION_CODENAME:?系统没有 VERSION_CODENAME}" >/etc/apt/sources.list.d/openresty.list
    apt-get -o DPkg::Lock::Timeout=300 update || die "apt-get update 失败（OpenResty 源不支持 ${ID} ${VERSION_CODENAME}？）"
    infra_apt_install openresty || die "openresty 安装失败"

    # 80 被别的进程占着就停下；nginx 配置里的端口要改，请直接改 conf/nginx/vpn.conf 的 listen。
    assert_port_free tcp 80 nginx NGINX_PORT_IN_VPN_CONF
    id web >/dev/null 2>&1 || useradd -r -m -s /usr/sbin/nologin web
    mkdir -p /home/file/nginx/cache/temp /home/file/nginx_cache/cache/body
    chown -R web:web /home/file/nginx /home/file/nginx_cache

    # 官方 systemd 单元里的 PIDFile 必须和 nginx.conf 的 pid 一致，否则 systemctl start 会超时。
    local conf="${OPENRESTY_PREFIX}/nginx/conf" src="${MYCONF_HOME}/conf/nginx" pidfile f
    pidfile="$(systemctl cat openresty 2>/dev/null | sed -n 's/^PIDFile=//p' | head -n 1)"
    [ -n "$pidfile" ] || pidfile="${OPENRESTY_PREFIX}/nginx/logs/nginx.pid"
    infra_put "${src}/nginx.conf" "${conf}/nginx.conf" 644 "s|^pid[[:space:]].*|pid ${pidfile};|"
    mkdir -p "${conf}/server"
    for f in nginx_check.conf upstream.conf vpn.conf; do
        infra_put "${src}/${f}" "${conf}/server/${f}" 644
    done

    "${OPENRESTY_PREFIX}/bin/openresty" -t || die "nginx 配置检查失败（旧配置已备份为 .bak 之类，见上面的输出）"
    svc_enable_restart openresty
    remind_security_group
    log "OpenResty 已启动: $("${OPENRESTY_PREFIX}/bin/openresty" -v 2>&1)"
    log "编进去的模块: ${OPENRESTY_PREFIX}/bin/openresty -V"
}

# ------------------------------------------------------------------ Redis

infra_redis() {
    require_root
    infra_need_apt
    infra_apt_install redis-server || die "redis-server 安装失败"
    local exprs=(
        's|^pidfile .*|pidfile /run/redis/redis-server.pid|'
        's|^logfile .*|logfile /var/log/redis/redis-server.log|'
        's|^dir .*|dir /var/lib/redis|'
        's|^supervised .*|supervised systemd|'
        '/^[[:space:]]*syslog-/d'
    )
    [ -z "${INFRA_REDIS_PASSWORD:-}" ] || exprs+=("s|^requirepass .*|requirepass ${INFRA_REDIS_PASSWORD}|")
    infra_put "${MYCONF_HOME}/conf/redis/redis.conf" /etc/redis/redis.conf 640 "${exprs[@]}"
    chown redis:redis /etc/redis/redis.conf
    svc_enable_restart redis-server
    log "Redis 已启动，监听 $(infra_ip):6380（端口取自 redis.conf）"
}

# ------------------------------------------------------------------ PostgreSQL

# PostgreSQL 来自官方 PGDG apt 源（签名验证）。jammy 自带的是 14，PG 17 是当前稳定版。
PG_VERSION="${PG_VERSION:-17}"
PG_PORT="${PG_PORT:-5432}"
PG_REPO="${PG_REPO:-https://apt.postgresql.org/pub/repos/apt}"
PG_KEY_URL="${PG_KEY_URL:-https://www.postgresql.org/media/keys/ACCC4CF8.asc}"
PG_ADMIN_PASSWORD="${PG_ADMIN_PASSWORD:-}"

# 内网段：从 INFRA_BIND（或本机内网地址）推出 /24。pg_hba 只允许这个段和本机。
infra_pg_net() {
    local ip
    ip="$(infra_ip)"
    case "$ip" in
        127.0.0.1) printf '127.0.0.1/32' ;;
        *) printf '%s.0/24' "$(printf '%s' "$ip" | cut -d. -f1-3)" ;;
    esac
}

infra_postgres() {
    require_root
    infra_need_apt
    [ "$(detect_arch)" = "amd64" ] || die "PGDG 源这里只验证过 amd64"
    # shellcheck disable=SC1091
    . /etc/os-release
    [ "${ID:-}" = "ubuntu" ] && [ "${VERSION_CODENAME:-}" = "jammy" ] \
        || die "PGDG 源按 Ubuntu 22.04 (jammy) 验证过，当前: ${ID:-?} ${VERSION_CODENAME:-?}"
    ensure_cmds gpg:gnupg curl
    local v="$PG_VERSION" key ip net listen unit="postgresql@${PG_VERSION}-main" conf_dir data_dir
    case "$v" in 1[3-9]) ;; *) die "PG_VERSION 不对: ${v}（如 17）" ;; esac

    key="$(mktemp "${TMPDIR:-/tmp}/pgdg-key.XXXXXX")" || die "无法创建临时文件"
    download "$PG_KEY_URL" "$key" || die "下载 PGDG 签名密钥失败"
    gpg --batch --yes --dearmor -o /usr/share/keyrings/pgdg.gpg "$key" || die "导入签名密钥失败"
    rm -f "$key"
    printf 'deb [signed-by=/usr/share/keyrings/pgdg.gpg] %s jammy-pgdg main\n' "$PG_REPO" \
        >/etc/apt/sources.list.d/pgdg.list
    apt-get -o DPkg::Lock::Timeout=300 update || die "apt-get update 失败（PGDG 源）"
    infra_apt_install "postgresql-${v}" "postgresql-client-${v}" || die "postgresql-${v} 安装失败"

    conf_dir="/etc/postgresql/${v}/main"
    data_dir="/var/lib/postgresql/${v}/main"
    [ -d "$conf_dir" ] || die "没有找到 ${conf_dir}，包结构和预期不一样"

    # 监听地址：INFRA_BIND 或本机内网地址；没有就只听本机。
    ip="$(infra_ip)"
    listen="$ip"
    [ "$ip" = "127.0.0.1" ] && listen="127.0.0.1"
    net="$(infra_pg_net)"

    # 服务端参数：放进 conf.d，不改包自带的 postgresql.conf。
    mkdir -p "${conf_dir}/conf.d"
    infra_put "${TEMPLATE_DIR}/postgres/postgresql.conf" "${conf_dir}/conf.d/90-vpn.conf" 644 \
        "s/{{LISTEN}}/${listen}/" "s/{{PORT}}/${PG_PORT}/"
    chown postgres:postgres "${conf_dir}/conf.d/90-vpn.conf"

    # 认证文件：整份替换为模板（旧文件备份）。
    infra_put "${TEMPLATE_DIR}/postgres/pg_hba.conf" "${conf_dir}/pg_hba.conf" 640 \
        "s|{{NET}}|${net}|"
    chown postgres:postgres "${conf_dir}/pg_hba.conf"

    mkdir -p /var/log/postgresql && chown postgres:postgres /var/log/postgresql

    # 数据目录只在第一次安装时由 pg_createcluster 创建（包已经做了），这里只保证它存在。
    [ -d "$data_dir" ] || die "数据目录 ${data_dir} 不存在，检查 pg_lsclusters"

    svc_enable_restart "$unit" || die "PostgreSQL 启动失败: journalctl -u ${unit} -n 30"
    # 等待就绪
    local i=0
    until su -s /bin/sh postgres -c "pg_isready -q -p ${PG_PORT}" 2>/dev/null; do
        i=$((i + 1)); [ "$i" -ge 30 ] && die "PostgreSQL 30 秒内没就绪: pg_lsclusters / journalctl -u ${unit}"
        sleep 1
    done

    # 管理员口令：只从 PG_ADMIN_PASSWORD 读。SQL 经标准输入传给 psql，不进命令行参数（ps 看不到），
    # 单引号在这里转义，口令里有 ' 也不会断句或注入。不写进任何文件，不打印。
    if [ -n "$PG_ADMIN_PASSWORD" ]; then
        local pw_sql
        pw_sql=$(printf '%s' "$PG_ADMIN_PASSWORD" | sed "s/'/''/g")
        if printf "ALTER USER postgres PASSWORD '%s';\n" "$pw_sql" \
            | su -s /bin/sh postgres -c "psql -q -v ON_ERROR_STOP=1 -f -" >/dev/null 2>&1; then
            log "postgres 口令已设置（来自 PG_ADMIN_PASSWORD，未显示）"
        else
            die "设置 postgres 口令失败（检查 PG_ADMIN_PASSWORD 或 journalctl -u ${unit}）"
        fi
    else
        warn "没有设置 postgres 口令：PG_ADMIN_PASSWORD=<口令> bash infra.sh postgres，或之后手动 ALTER USER"
    fi
    remind_security_group
    log "PostgreSQL ${v} 已启动: 监听 ${listen}:${PG_PORT}，允许网段 ${net} + 本机，全部 scram-sha-256"
    log "连接: psql -h ${ip} -p ${PG_PORT} -U postgres"
}

# ------------------------------------------------------------------ MySQL

# 保持旧的安装方式（官方 tarball，版本固定）以便和线上一致；升级版本是另一件事，见最后的说明。
infra_mysql() {
    require_root
    infra_need_apt
    local v="$MYSQL_VERSION" name dest ip
    name="mysql-${v}-linux-glibc2.12-x86_64"
    dest="${INFRA_OPT}/mysql-${v}"
    infra_apt_install libaio1 libnuma1 libncurses5 perl || die "依赖安装失败"
    id mysql >/dev/null 2>&1 || useradd -r -m -d /home/mysql -s /bin/bash mysql
    if [ ! -d "$dest" ]; then
        mkdir -p "$TMP_HOME" "$INFRA_OPT"
        download "https://cdn.mysql.com/archives/mysql-5.6/${name}.tar.gz" "${TMP_HOME}/${name}.tar.gz" \
            || die "下载 MySQL ${v} 失败"
        tar -xzf "${TMP_HOME}/${name}.tar.gz" -C "$INFRA_OPT" && mv "${INFRA_OPT}/${name}" "$dest" \
            || die "解压失败"
        chown -R root:root "$dest"
    fi
    ln -sfn "$dest" /usr/local/mysql
    mkdir -p "$MYSQL_DATADIR" /home/mysql/log_data /var/log/mysql /var/run/mysqld /var/lib/mysql /usr/share/mysql
    chown mysql:mysql "$MYSQL_DATADIR" /home/mysql/log_data /var/log/mysql /var/run/mysqld /var/lib/mysql

    ip="$(infra_ip)"
    if [ "${INFRA_MYSQL_PUBLIC:-0}" = "1" ]; then
        infra_put "${MYCONF_HOME}/conf/mysql/my.cnf" /etc/my.cnf 640
    else
        infra_put "${MYCONF_HOME}/conf/mysql/my.cnf" /etc/my.cnf 640 "s/^\(bind-address[[:space:]]*=[[:space:]]*\)0\.0\.0\.0/\1${ip}/"
    fi
    chgrp mysql /etc/my.cnf
    cp "${dest}/share/english/errmsg.sys" /usr/share/mysql/

    # 数据目录里已有 mysql 库就绝不重新初始化（旧脚本这里是 rm -rf db_data/*）。
    if [ -d "${MYSQL_DATADIR}/mysql" ]; then
        log "数据目录已有数据，跳过初始化（${MYSQL_DATADIR}）"
    else
        (cd "$dest" && scripts/mysql_install_db --user=mysql --basedir="$dest" --datadir="$MYSQL_DATADIR") \
            || die "mysql_install_db 失败"
        warn "root 初始没有密码。先设置: /usr/local/mysql/bin/mysqladmin -u root password '<新密码>'"
    fi
    install_template "${TEMPLATE_DIR}/mysql/mysql.service" /etc/systemd/system/mysql.service 644 "MYSQL_VERSION=${v}"
    svc_enable_restart mysql
    log "MySQL ${v} 已启动（systemd: mysql）"
}

# ------------------------------------------------------------------ FreeRADIUS

# FreeRADIUS 3.2.x，来自 NetworkRadius 官方 apt 源（jammy 上最新 3.2.10，已签名）。
# 只装包、放自定义的 sql 模块和 clients.conf；2.x 的配置文件格式和 3.x 不兼容，不能整套覆盖。
# 日常的 clients.conf 更新和重启用 radius.sh。
RADIUS_REPO_BASE="${RADIUS_REPO_BASE:-https://packages.networkradius.com/freeradius-3.2/ubuntu/jammy}"
RADIUS_ETC=/etc/freeradius/3.0

infra_radius() {
    require_root
    infra_need_apt
    [ "$(detect_arch)" = "amd64" ] || die "NetworkRadius 3.2 jammy 源这里只验证过 amd64"
    # shellcheck disable=SC1091
    . /etc/os-release
    [ "${VERSION_CODENAME:-}" = "jammy" ] || die "这个脚本按 Ubuntu 22.04 (jammy) 写的，当前: ${VERSION_CODENAME:-unknown}"
    ensure_cmds gpg:gnupg curl

    local key
    key="$(mktemp "${TMPDIR:-/tmp}/nr-key.XXXXXX")" || die "无法创建临时文件"
    download "https://packages.networkradius.com/pgp/packages%40networkradius.com" "$key" \
        || die "下载 NetworkRadius 签名密钥失败"
    gpg --batch --yes --dearmor -o /usr/share/keyrings/networkradius.gpg "$key" || die "导入签名密钥失败"
    rm -f "$key"
    printf 'deb [signed-by=/usr/share/keyrings/networkradius.gpg] %s jammy main\n' "$RADIUS_REPO_BASE" \
        >/etc/apt/sources.list.d/networkradius.list
    apt-get -o DPkg::Lock::Timeout=300 update || die "apt-get update 失败"
    infra_apt_install freeradius freeradius-mysql freeradius-utils || die "freeradius 安装失败"

    [ -d "$RADIUS_ETC" ] || die "没有找到 ${RADIUS_ETC}，包结构和预期不一样"
    # 自定义 sql 模块：数据库地址、账号、密码取自 conf/radius/sql.conf 的 sql {} 段。
    # 只改这一个模块的 server/port/login/password/radius_db，其它保持包自带的默认值。
    radius_install_sql_module
    # clients.conf 是唯一会经常改的文件，交给 radius.sh clients 管理（会校验后再重载）。
    install_file "${MYCONF_HOME}/conf/radius/clients.conf" "${RADIUS_ETC}/clients.conf" 640
    chgrp freerad "${RADIUS_ETC}/clients.conf" 2>/dev/null || true

    # 用包自带的配置做语法检查，失败就不启动。
    freeradius -XC -d "$RADIUS_ETC" >/dev/null 2>&1 || die "配置检查失败，运行: freeradius -XC -d ${RADIUS_ETC} 看具体错误"
    svc_enable_restart freeradius
    log "FreeRADIUS $(freeradius -v 2>/dev/null | head -n 1 | grep -oE '[0-9.]+' | head -n 1) 已启动（systemd: freeradius）"
    log "日常更新 clients.conf 和重启: bash radius.sh clients"
}

# 把 conf/radius/sql.conf 里的数据库连接参数写进 3.x 的 mods-available/sql，并在 default 站点里启用 sql。
radius_install_sql_module() {
    local src="${MYCONF_HOME}/conf/radius/sql.conf" dst="${RADIUS_ETC}/mods-available/sql" host port login pass db
    [ -f "$src" ] || die "缺少 ${src}"
    host="$(sed -n 's/^[[:space:]]*server[[:space:]]*=[[:space:]]*"\(.*\)".*/\1/p' "$src" | head -n 1)"
    port="$(sed -n 's/^[[:space:]]*port[[:space:]]*=[[:space:]]*\([0-9]*\).*/\1/p' "$src" | head -n 1)"
    login="$(sed -n 's/^[[:space:]]*login[[:space:]]*=[[:space:]]*"\(.*\)".*/\1/p' "$src" | head -n 1)"
    pass="$(sed -n 's/^[[:space:]]*password[[:space:]]*=[[:space:]]*"\(.*\)".*/\1/p' "$src" | head -n 1)"
    db="$(sed -n 's/^[[:space:]]*radius_db[[:space:]]*=[[:space:]]*"\(.*\)".*/\1/p' "$src" | head -n 1)"
    [ -n "$host" ] && [ -n "$login" ] && [ -n "$pass" ] || die "conf/radius/sql.conf 里读不到数据库连接参数"
    [ -f "$dst" ] || die "没有 ${dst}（freeradius-mysql 没装上？）"
    local tmp
    tmp="$(mktemp "${TMPDIR:-/tmp}/sqlmod.XXXXXX")" || die "无法创建临时文件"
    sed -e "s|^\([[:space:]]*server[[:space:]]*=\).*|\1 \"${host}\"|" \
        -e "s|^\([[:space:]]*port[[:space:]]*=\).*|\1 ${port:-3306}|" \
        -e "s|^\([[:space:]]*login[[:space:]]*=\).*|\1 \"${login}\"|" \
        -e "s|^\([[:space:]]*password[[:space:]]*=\).*|\1 \"${pass}\"|" \
        -e "s|^\([[:space:]]*radius_db[[:space:]]*=\).*|\1 \"${db:-radius}\"|" \
        "$dst" >"$tmp"
    install_file "$tmp" "$dst" 640
    rm -f "$tmp"
    chgrp freerad "$dst" 2>/dev/null || true
    mkdir -p "${RADIUS_ETC}/mods-enabled"
    ln -sfn ../mods-available/sql "${RADIUS_ETC}/mods-enabled/sql"
    # 3.x 包自带的站点里 sql 是注释掉的，不挂上就不会查数据库，认证只会走 users 文件。
    # 把 authorize / accounting / session / post-auth 段里的 "#  sql" 取消注释（只动这几行）。
    local site
    for site in default inner-tunnel; do
        [ -f "${RADIUS_ETC}/sites-enabled/${site}" ] || continue
        local tmp
        tmp="$(mktemp "${TMPDIR:-/tmp}/site.XXXXXX")" || die "无法创建临时文件"
        sed -E 's/^([[:space:]]*)#[[:space:]]*sql[[:space:]]*$/\1sql/' "${RADIUS_ETC}/sites-enabled/${site}" >"$tmp"
        install_file "$tmp" "${RADIUS_ETC}/sites-enabled/${site}" 640
        rm -f "$tmp"
        grep -qE '^[[:space:]]*sql[[:space:]]*$' "${RADIUS_ETC}/sites-enabled/${site}" \
            || warn "${site} 站点里没有找到可以启用的 sql 行，请检查包的默认配置"
    done
    # 密码和账号不在日志里出现
    log "sql 模块已指向 ${host}:${port:-3306}（库 ${db:-radius}，账号已写入，未显示）"
}

# ------------------------------------------------------------------ PHP

# PHP 版本：默认 8.4（当前稳定、仍在安全支持期内；jammy 自带的 8.1 已停止维护）。
# 来自 Ondřej Surý 的 packages.sury.org 源（签名验证），jammy 上 8.1–8.5 都有。
PHP_VERSION="${PHP_VERSION:-8.4}"
PHP_REPO="${PHP_REPO:-https://packages.sury.org/php}"
PHP_POOL_USER="${PHP_POOL_USER:-web}"

infra_php() {
    require_root
    infra_need_apt
    [ "$(detect_arch)" = "amd64" ] || die "PHP 源这里只验证过 amd64"
    # shellcheck disable=SC1091
    . /etc/os-release
    [ "${ID:-}" = "ubuntu" ] && [ "${VERSION_CODENAME:-}" = "jammy" ] \
        || die "PHP 源按 Ubuntu 22.04 (jammy) 验证过，当前: ${ID:-?} ${VERSION_CODENAME:-?}"
    ensure_cmds gpg:gnupg curl
    local v="$PHP_VERSION" fpm="php${PHP_VERSION}-fpm" key pkgs tmp
    case "$v" in 8.[0-9] | 8.[0-9][0-9]) ;; *) die "PHP_VERSION 格式不对: ${v}（如 8.4）" ;;
    esac

    key="$(mktemp "${TMPDIR:-/tmp}/sury-key.XXXXXX")" || die "无法创建临时文件"
    download "${PHP_REPO}/apt.gpg" "$key" || die "下载 PHP 源签名密钥失败"
    gpg --batch --yes --dearmor -o /usr/share/keyrings/sury-php.gpg "$key" || die "导入签名密钥失败"
    rm -f "$key"
    printf 'deb [signed-by=/usr/share/keyrings/sury-php.gpg] %s jammy main\n' "$PHP_REPO" \
        >/etc/apt/sources.list.d/sury-php.list
    apt-get -o DPkg::Lock::Timeout=300 update || die "apt-get update 失败（PHP 源）"

    pkgs="php${v}-cli php${v}-fpm php${v}-mysql php${v}-mbstring php${v}-xml php${v}-curl php${v}-gd \
php${v}-zip php${v}-intl php${v}-bcmath php${v}-opcache unzip"
    # shellcheck disable=SC2086
    infra_apt_install $pkgs || die "PHP ${v} 安装失败"

    # 通用设置：fpm 和 cli 各放一份，参数一致。
    for tmp in fpm cli; do
        install_file "${TEMPLATE_DIR}/php/99-vpn.ini" "/etc/php/${v}/${tmp}/conf.d/99-vpn.ini" 644
    done

    # 进程池：web 用户。默认的 www 池停用（改名保留，不删）。
    id "$PHP_POOL_USER" >/dev/null 2>&1 || useradd -r -m -s /usr/sbin/nologin "$PHP_POOL_USER"
    mkdir -p /var/log/php-fpm "/etc/php/${v}/fpm/pool.d" /run/php
    chown "${PHP_POOL_USER}:${PHP_POOL_USER}" /var/log/php-fpm
    if [ -f "/etc/php/${v}/fpm/pool.d/www.conf" ]; then
        mv -f "/etc/php/${v}/fpm/pool.d/www.conf" "/etc/php/${v}/fpm/pool.d/www.conf.disabled"
    fi
    install_file "${TEMPLATE_DIR}/php/web-pool.conf" "/etc/php/${v}/fpm/pool.d/web.conf" 644

    # composer（ss-panel 用）：官方安装器装到 /usr/local/bin。
    if ! have composer; then
        tmp="$(mktemp -d "${TMPDIR:-/tmp}/composer.XXXXXX")" || die "无法创建临时目录"
        download "https://getcomposer.org/installer" "${tmp}/installer.php" || die "下载 composer 安装器失败"
        (cd "$tmp" && php installer.php --install-dir=/usr/local/bin --filename=composer --quiet) \
            || die "composer 安装失败"
        rm -rf "$tmp"
    fi

    php-fpm"${v}" -t >/dev/null 2>&1 || die "php-fpm 配置检查失败: php-fpm${v} -t"
    svc_enable_restart "$fpm"
    remind_security_group
    log "PHP ${v} 已启动（$(php -v | head -n 1 | cut -d' ' -f1-2)，composer $(composer --version 2>/dev/null | grep -oE '[0-9.]+' | head -n 1)）"
    log "php-fpm 池 ${PHP_POOL_USER}: /run/php/php-fpm-web.sock（nginx 用 fastcgi_pass unix:... 接入）"
}

# ------------------------------------------------------------------ JDK / Maven

infra_jdk() {
    require_root
    infra_need_apt
    infra_apt_install "$INFRA_JDK_PKG" maven || die "JDK / Maven 安装失败"
    log "$(java -version 2>&1 | head -n 1)；$(mvn -v 2>/dev/null | head -n 1)"
}

# ------------------------------------------------------------------ 入口

infra_main() {
    local action="${1:-}"
    case "$action" in
        nginx) infra_nginx ;;
        redis) infra_redis ;;
        postgres | pg) infra_postgres ;;
        mysql) infra_mysql ;;
        radius) infra_radius ;;
        jdk) infra_jdk ;;
        php) infra_php ;;
        all)
            infra_mysql
            infra_radius
            infra_nginx
            infra_redis
            infra_jdk
            infra_php
            infra_postgres
            ;;
        '' | help | -h | --help) infra_usage ;;
        *)
            err "未知软件: ${action}"
            infra_usage
            return 2
            ;;
    esac
}

infra_main "$@"
