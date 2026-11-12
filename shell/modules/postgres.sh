#!/usr/bin/env bash
# PostgreSQL 的安装、启停、超级用户和业务库（薄封装）。
#
# 用法（通过 vpn.sh 调用）：
#   vpn.sh postgres setup            首次安装：装包 + 建角色 + 建库 + 授权（可重复运行）
#   vpn.sh postgres install          只装包和基础配置（内部调用 infra.sh postgres）
#   vpn.sh postgres roles            创建/更新超级用户 root、sspacee（口令不落盘、不回显）
#   vpn.sh postgres db               创建库 uher 并授权给 root、sspacee
#   vpn.sh postgres start|stop|restart|status
#   vpn.sh postgres check            服务、端口、角色、库、数据目录权限自检
#
# 设计说明：
#   - 安装和 postgresql.conf / pg_hba.conf 的唯一来源是 infra.sh postgres，这里不重复实现，
#     只做"装好之后还要什么"的部分，避免两份配置漂移。
#   - 数据库里一律使用系统包自带的 postgres 用户（Debian 包创建的系统用户，不是 root），
#     数据目录 /var/lib/postgresql/<版本>/<cluster> 只属于它。
#   - 角色、口令、授权不在本文件里：唯一来源是 conf/postgres/init.sql，
#     由 shell/dbinit.sh 执行。安装和账号管理分开，装完不用重跑安装，
#     改口令只改 init.sql 再跑 `bash dbinit.sh postgres`。
#   - 所有 SQL 都是幂等的：角色存在就 ALTER 对齐权限，库存在就跳过创建。
#
# 详见 docs/postgres.md。

PG_VERSION="${PG_VERSION:-17}"
PG_PORT="${PG_PORT:-5432}"
# 超级用户清单：默认 root 和 sspacee，都是 SUPERUSER + CREATEDB + CREATEROLE。
# 仅用于状态显示和自检；真正建角色的是 conf/postgres/init.sql。
PG_SUPER_ROLES="${PG_SUPER_ROLES:-root sspacee}"
# 业务库清单，空格分隔；check 会逐个核对。真正建库的是 dbinit.sh。
PG_DBS="${PG_DBS:-uher job_come}"
PG_DB_OWNER="${PG_DB_OWNER:-sspacee}"
# 兼容旧的单库变量：只用于 setup 结束时的连接串提示。
PG_DB="${PG_DB:-${PG_DBS%% *}}"
# 口令文件，init.sql 里若改成从文件读取时用得到（当前 init.sql 直接写口令）。
PG_SECRET_FILE="${PG_SECRET_FILE:-${MYCONF_HOME}/conf/postgres/.env}"

postgres_usage() {
    cat <<EOF
PostgreSQL 模块:
  setup               首次安装一条龙：install + roles + db（可重复运行）
  install             安装 PostgreSQL ${PG_VERSION}（PGDG 源）并校验系统用户/数据目录
  roles               执行 conf/postgres/init.sql 建角色（等同 bash dbinit.sh postgres）
  db                  建库 ${PG_DBS}（owner ${PG_DB_OWNER}）并授权（同上）
  start | stop | restart | status
  check               服务、端口、pg_hba、角色、库、数据目录权限自检

环境变量:
  PG_VERSION          版本，默认 ${PG_VERSION}
  PG_PORT             端口，默认 ${PG_PORT}
  PG_SUPER_ROLES      超级用户，默认 "${PG_SUPER_ROLES}"（仅用于自检）
  PG_DBS              业务库，空格分隔，默认 "${PG_DBS}"
  PG_DB_OWNER         业务库 owner，默认 ${PG_DB_OWNER}

口令和授权: 改 conf/postgres/init.sql，然后 bash dbinit.sh postgres
口令不会打印、不会写进日志。写进 init.sql 的值会进入 git 历史。

文档: docs/postgres.md
EOF
}

# ------------------------------------------------------------------ 集群识别

# 从 pg_lsclusters 里挑一个集群：优先 online 的，其次第一个。
pg_cluster_info() {
    PG_CLUSTER_VER=""
    PG_CLUSTER_NAME=""
    PG_CLUSTER_PORT=""
    PG_CLUSTER_STATUS=""

    have pg_lsclusters || return 1
    local row
    row="$(pg_lsclusters --no-header 2>/dev/null | awk '$4 == "online" { print; exit }')"
    [ -n "$row" ] || row="$(pg_lsclusters --no-header 2>/dev/null | head -n 1)"
    [ -n "$row" ] || return 1

    PG_CLUSTER_VER="$(printf '%s\n' "$row" | awk '{print $1}')"
    PG_CLUSTER_NAME="$(printf '%s\n' "$row" | awk '{print $2}')"
    PG_CLUSTER_PORT="$(printf '%s\n' "$row" | awk '{print $3}')"
    PG_CLUSTER_STATUS="$(printf '%s\n' "$row" | awk '{print $4}')"
    [ -n "$PG_CLUSTER_NAME" ] || return 1
    return 0
}

pg_installed() {
    pg_cluster_info >/dev/null 2>&1
}

pg_unit() {
    printf 'postgresql@%s-%s' "$PG_CLUSTER_VER" "$PG_CLUSTER_NAME"
}

pg_conf_dir() {
    printf '/etc/postgresql/%s/%s' "$PG_CLUSTER_VER" "$PG_CLUSTER_NAME"
}

pg_data_dir() {
    printf '/var/lib/postgresql/%s/%s' "$PG_CLUSTER_VER" "$PG_CLUSTER_NAME"
}

# 需要集群信息才能继续；没装就给出下一步。
pg_require_cluster() {
    if ! pg_cluster_info; then
        die "没有发现 PostgreSQL 集群（pg_lsclusters 为空）。先安装: bash vpn.sh postgres install"
    fi
}

# 以系统用户 postgres 走本地 socket（pg_hba.local postgres = peer），SQL 从标准输入进。
# 口令和 SQL 都不进命令行参数，ps 看不到。
pg_admin_psql() { # [库名]
    local db="${1:-postgres}"
    case "$db" in
        '' | *[!A-Za-z0-9_]*) die "非法库名: ${db}" ;;
    esac
    su -s /bin/sh postgres -c "psql -q -v ON_ERROR_STOP=1 -d ${db} -f -"
}

# 单值查询，返回一行。SQL 也走标准输入。
pg_admin_query() {
    su -s /bin/sh postgres -c "psql -tAq -v ON_ERROR_STOP=1 -d postgres -f -"
}

# 服务是否就绪；pg_isready 只探测端口，不需要口令，普通用户也能跑。
pg_ready() {
    local port="${PG_CLUSTER_PORT:-$PG_PORT}"
    if have pg_isready; then
        pg_isready -q -h 127.0.0.1 -p "$port" 2>/dev/null && return 0
        pg_isready -q -p "$port" 2>/dev/null && return 0
        return 1
    fi
    [ "$(id -u)" -eq 0 ] || return 1
    su -s /bin/sh postgres -c "pg_isready -q -p ${port}" 2>/dev/null
}

# ------------------------------------------------------------------ 角色与库

# ------------------------------------------------------------------ 系统用户与数据目录

# PostgreSQL 必须以独立系统用户 postgres 运行，数据目录只给它。
# Debian/Ubuntu 的包会自动建这个用户；这里只兜底 + 校验，权限不对就停下来说清楚。
postgres_assert_user() {
    local data_dir mode owner
    data_dir="$(pg_data_dir)"

    if ! id postgres >/dev/null 2>&1; then
        warn "系统用户 postgres 不存在，按系统用户创建（不带登录 shell）"
        useradd --system --create-home --home-dir /var/lib/postgresql \
            --shell /usr/sbin/nologin postgres || die "创建系统用户 postgres 失败"
    fi

    [ -d "$data_dir" ] || die "数据目录 ${data_dir} 不存在。检查: pg_lsclusters / dpkg -l 'postgresql-*'"

    owner="$(stat -c '%U' "$data_dir")"
    mode="$(stat -c '%a' "$data_dir")"
    if [ "$owner" != "postgres" ]; then
        if [ -n "${PG_FIX_OWNER:-}" ]; then
            warn "数据目录 ${data_dir} 属于 ${owner}，按 PG_FIX_OWNER=1 交给 postgres"
            chown -R postgres:postgres "$data_dir" || die "chown ${data_dir} 失败"
        else
            die "数据目录 ${data_dir} 属于 ${owner}，不是 postgres。确认无人在用后执行: chown -R postgres:postgres ${data_dir}（或设置 PG_FIX_OWNER=1 让脚本处理）"
        fi
    fi
    case "$mode" in
        700) ;;
        *)
            warn "数据目录 ${data_dir} 权限是 ${mode}，收回成 700"
            chmod 700 "$data_dir" || warn "chmod 700 ${data_dir} 失败，请手工处理"
            ;;
    esac
    log "系统用户 postgres，数据目录 $(pg_data_dir)（owner postgres，700）"
}

# ------------------------------------------------------------------ 安装

postgres_install() {
    require_root

    if pg_installed; then
        log "PostgreSQL 已安装（集群 ${PG_CLUSTER_VER}/${PG_CLUSTER_NAME}，状态 ${PG_CLUSTER_STATUS}），跳过装包"
    else
        [ -f "${VPN_SHELL_DIR}/infra.sh" ] || die "缺少 infra.sh，无法安装 PostgreSQL"
        log "调用 infra.sh postgres 安装 PostgreSQL ${PG_VERSION}（PGDG 源）"
        # 口令只经环境变量往下传，不进命令行参数；没设就不传，免得 infra.sh 报一句无用的告警。
        if [ -n "${PG_ADMIN_PASSWORD:-}" ]; then
            PG_ADMIN_PASSWORD="$PG_ADMIN_PASSWORD" bash "${VPN_SHELL_DIR}/infra.sh" postgres \
                || die "PostgreSQL 安装失败，见上面的输出"
        else
            bash "${VPN_SHELL_DIR}/infra.sh" postgres || die "PostgreSQL 安装失败，见上面的输出"
        fi
    fi

    pg_require_cluster
    postgres_assert_user

    if [ "$PG_CLUSTER_STATUS" != "online" ]; then
        warn "集群 ${PG_CLUSTER_VER}/${PG_CLUSTER_NAME} 当前是 ${PG_CLUSTER_STATUS}，尝试启动"
        postgres_act start || die "启动失败: journalctl -u $(pg_unit) -n 30"
    fi
    log "PostgreSQL ${PG_CLUSTER_VER} 已就绪: 端口 ${PG_CLUSTER_PORT:-$PG_PORT}，配置文件 $(pg_conf_dir)"
}

# ------------------------------------------------------------------ 角色与库

postgres_roles() {
    require_root
    pg_require_cluster
    postgres_assert_user

    # 角色定义和口令都在 conf/postgres/init.sql，由 dbinit.sh 统一执行。
    # 这样账号管理和其他数据库放在一起，装完不用重跑安装。
    local script="${VPN_SHELL_DIR}/dbinit.sh"
    [ -f "$script" ] || die "缺少 ${script}"
    bash "$script" postgres || return 1
    log "角色的定义在 conf/postgres/init.sql（改完重跑: bash dbinit.sh postgres）"
}

postgres_db() {
    require_root
    pg_require_cluster
    postgres_assert_user

    # 建库和授权都在 dbinit.sh 里（它先保证库存在，再执行 init.sql 的 GRANT）。
    local script="${VPN_SHELL_DIR}/dbinit.sh"
    [ -f "$script" ] || die "缺少 ${script}"
    bash "$script" postgres || return 1
}

postgres_setup() {
    postgres_install
    postgres_roles
    postgres_db
    log "完成。连接串: postgresql://<用户>@$(pg_listen_addr):${PG_CLUSTER_PORT:-$PG_PORT}/${PG_DB}"
    log "详细运维说明见 docs/postgres.md"
}

# ------------------------------------------------------------------ 服务

# 配置里的监听地址，取 ip 或 listen_addresses 的第一项。
pg_listen_addr() {
    local conf_dir addr
    conf_dir="$(pg_conf_dir)"
    addr="$(sed -n "s/^[[:space:]]*listen_addresses[[:space:]]*=[[:space:]]*'\([^']*\)'.*/\1/p" \
        "${conf_dir}/conf.d/90-vpn.conf" 2>/dev/null | head -n 1)"
    if [ -z "$addr" ]; then
        addr="$(sed -n "s/^[[:space:]]*listen_addresses[[:space:]]*=[[:space:]]*\([^#]*\).*/\1/p" \
            "${conf_dir}/postgresql.conf" 2>/dev/null | head -n 1 | tr -d "' \"")"
    fi
    # 两处都没写：PostgreSQL 自身的默认值是 localhost，不是"未配置"。
    # 这种情况出现在机器上原本就有一套独立安装的 PostgreSQL、没跑过 infra.sh 的时候。
    [ -n "$addr" ] || addr="localhost"
    printf '%s\n' "${addr%%,*}"
}

postgres_act() { # start|stop|restart
    local act="$1"
    require_root
    pg_require_cluster

    # 优先 pg_ctlcluster：Debian/Ubuntu 的集群工具，会自动带上 -D 和配置路径。
    if have pg_ctlcluster; then
        pg_ctlcluster "$PG_CLUSTER_VER" "$PG_CLUSTER_NAME" "$act" || {
            err "${act} ${PG_CLUSTER_VER}/${PG_CLUSTER_NAME} 失败: journalctl -u $(pg_unit) -n 30"
            return 1
        }
    else
        systemctl "$act" "$(pg_unit)" || {
            err "${act} $(pg_unit) 失败: journalctl -u $(pg_unit) -n 30"
            return 1
        }
    fi
    log "${act} 完成（${PG_CLUSTER_VER}/${PG_CLUSTER_NAME}）"
    # stop 之后 status 本来就该报"没在监听"，不能因此让整个命令失败。
    case "$act" in
        start)
            postgres_wait_ready
            postgres_status
            ;;
        restart) postgres_status ;;
        stop)
            postgres_status || true
            ;;
    esac
}

postgres_wait_ready() {
    local i=0
    until pg_ready; do
        i=$((i + 1))
        [ "$i" -ge 30 ] && die "30 秒内没就绪: pg_lsclusters / journalctl -u $(pg_unit) -n 30"
        sleep 1
    done
    log "pg_isready: 已接受连接（端口 ${PG_CLUSTER_PORT:-$PG_PORT}）"
}

postgres_status() {
    # 重新读一遍集群状态：start/stop 之后调用时，缓存里的状态已经过时。
    pg_cluster_info >/dev/null 2>&1 || pg_require_cluster

    local act en listen pp
    act="$(systemctl is-active "$(pg_unit)" 2>/dev/null | head -n 1)"
    en="$(systemctl is-enabled "$(pg_unit)" 2>/dev/null | head -n 1)"
    pp="$(pg_listen_addr)"

    printf '集群: %s/%s  端口 %s  状态 %s\n' \
        "$PG_CLUSTER_VER" "$PG_CLUSTER_NAME" "${PG_CLUSTER_PORT:-$PG_PORT}" "$PG_CLUSTER_STATUS"
    printf '服务: %s  自启:%s  监听 %s:%s\n' \
        "${act:-未知}" "$([ "$en" = enabled ] && echo 是 || echo "${en:-否}")" \
        "${pp:-?}" "${PG_CLUSTER_PORT:-$PG_PORT}"
    listen="$(port_listeners tcp "${PG_CLUSTER_PORT:-$PG_PORT}")"
    if [ -n "$listen" ]; then
        printf '%s\n' "$listen"
    else
        printf '（没有进程在监听 tcp/%s）\n' "${PG_CLUSTER_PORT:-$PG_PORT}"
    fi
    if pg_ready; then
        printf 'pg_isready: 正常\n'
        return 0
    fi
    warn "pg_isready 失败，服务没在正常接受连接"
    return 1
}

# ------------------------------------------------------------------ 自检

postgres_check() {
    require_root
    pg_require_cluster
    local rc=0 role db owner mode

    echo "== 集群 =="
    pg_lsclusters 2>/dev/null || echo "  pg_lsclusters 不可用"
    postgres_status || rc=1

    echo "== 系统用户与数据目录 =="
    if id postgres >/dev/null 2>&1; then
        printf '  用户 postgres: %s\n' "$(getent passwd postgres | cut -d: -f6-7)"
    else
        printf '  %s\n' "用户 postgres 不存在"; rc=1
    fi
    owner="$(stat -c '%U:%G' "$(pg_data_dir)" 2>/dev/null)"
    mode="$(stat -c '%a' "$(pg_data_dir)" 2>/dev/null)"
    printf '  %s owner %s 权限 %s\n' "$(pg_data_dir)" "${owner:-?}" "${mode:-?}"
    [ "${owner%%:*}" = "postgres" ] || { printf '  数据目录不属于 postgres\n'; rc=1; }
    [ "$mode" = "700" ] || printf '  建议权限 700（当前 %s）\n' "${mode:-?}"

    echo "== 认证 =="
    grep -vE '^[[:space:]]*(#|$)' "$(pg_conf_dir)/pg_hba.conf" 2>/dev/null || echo "  读不到 pg_hba.conf"

    echo "== 角色 =="
    for role in $PG_SUPER_ROLES; do
        db="$(printf "SELECT CASE WHEN rolsuper AND rolcreatedb AND rolcreaterole AND rolcanlogin THEN 'ok' ELSE 'wrong' END FROM pg_roles WHERE rolname = '%s';\n" "$role" | pg_admin_query | head -n 1)"
        case "$db" in
            ok) printf '  %-10s SUPERUSER CREATEDB CREATEROLE LOGIN\n' "$role" ;;
            wrong) printf '  %-10s 权限不完整，重跑: bash vpn.sh postgres roles\n' "$role"; rc=1 ;;
            *) printf '  %-10s 不存在，重跑: bash vpn.sh postgres roles\n' "$role"; rc=1 ;;
        esac
    done

    echo "== 数据库 =="
    for db in ${PG_DBS:-uher}; do
        printf "SELECT datname || ' owner=' || pg_get_userbyid(datdba) FROM pg_database WHERE datname = '%s';\n" "$db" \
            | pg_admin_query | sed 's/^/  /'
    done
    printf "SELECT 'database_count=' || count(*) FROM pg_database WHERE datallowconn;\n" | pg_admin_query | sed 's/^/  /'

    echo "== 磁盘 =="
    df -h "$(pg_data_dir)" 2>/dev/null | tail -n 1 | sed 's/^/  /'

    [ "$rc" -eq 0 ] || warn "自检发现问题，见上面"
    return "$rc"
}

# ------------------------------------------------------------------ 入口

postgres_main() {
    local action="${1:-}"
    [ $# -gt 0 ] && shift
    case "$action" in
        setup | all) postgres_setup ;;
        install) postgres_install ;;
        roles | users) postgres_roles ;;
        db | database) postgres_db ;;
        start | stop | restart) postgres_act "$action" ;;
        status) postgres_status ;;
        check) postgres_check ;;
        '' | help | -h | --help) postgres_usage ;;
        *)
            err "未知动作: ${action}"
            postgres_usage
            return 2
            ;;
    esac
}
