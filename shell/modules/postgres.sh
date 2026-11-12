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
#   - 口令只从环境变量 PG_SUPER_PASSWORD 或 conf/postgres/.env（已被 .gitignore 覆盖）读取，
#     通过 psql 的标准输入传给服务器：不进命令行参数（ps 看不到）、不写日志、不回显。
#     仓库里不保存任何口令。
#   - 所有 SQL 都是幂等的：角色存在就 ALTER 对齐权限，库存在就跳过创建。
#
# 详见 docs/postgres.md。

PG_VERSION="${PG_VERSION:-17}"
PG_PORT="${PG_PORT:-5432}"
# 超级用户清单：默认 root 和 sspacee，都是 SUPERUSER + CREATEDB + CREATEROLE。
PG_SUPER_ROLES="${PG_SUPER_ROLES:-root sspacee}"
# 业务库，owner 默认给 sspacee；root 是超级用户，另外再显式授权一次。
PG_DB="${PG_DB:-uher}"
PG_DB_OWNER="${PG_DB_OWNER:-sspacee}"
# 口令来源：环境变量优先，其次这个本地文件（.gitignore 里的 .env 规则覆盖它）。
PG_SECRET_FILE="${PG_SECRET_FILE:-${MYCONF_HOME}/conf/postgres/.env}"
PG_SUPER_PASSWORD="${PG_SUPER_PASSWORD:-}"

postgres_usage() {
    cat <<EOF
PostgreSQL 模块:
  setup               首次安装一条龙：install + roles + db（可重复运行）
  install             安装 PostgreSQL ${PG_VERSION}（PGDG 源）并校验系统用户/数据目录
  roles               创建或更新超级用户: ${PG_SUPER_ROLES}
  db                  创建库 ${PG_DB}（owner ${PG_DB_OWNER}），授权给 ${PG_SUPER_ROLES}
  start | stop | restart | status
  check               服务、端口、pg_hba、角色、库、数据目录权限自检

环境变量:
  PG_VERSION          版本，默认 ${PG_VERSION}
  PG_PORT             端口，默认 ${PG_PORT}
  PG_SUPER_ROLES      超级用户，默认 "${PG_SUPER_ROLES}"
  PG_DB               业务库，默认 ${PG_DB}
  PG_DB_OWNER         业务库 owner，默认 ${PG_DB_OWNER}
  PG_SUPER_PASSWORD   超级用户口令；不设则读 ${PG_SECRET_FILE}（只读，不执行文件内容）
  PG_SECRET_FILE      口令文件路径，默认 ${PG_SECRET_FILE}（.gitignore 已覆盖）
  PG_ADMIN_PASSWORD   可选：同时设置 postgres 账号口令（默认走 peer 认证，不设）

注意: 口令不会打印、不会写进日志。不要用 PG_SUPER_PASSWORD=... 直接写在命令行里，
      那会留在 shell 历史里；用 export、read -s 或口令文件。

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

# ------------------------------------------------------------------ 口令

# 只解析 PG_SUPER_PASSWORD=... 这一行，不 source 文件：口令文件里出现命令也不会被执行。
pg_load_password() {
    [ -n "${PG_SUPER_PASSWORD:-}" ] && return 0
    [ -f "$PG_SECRET_FILE" ] || return 1

    local line val
    line="$(grep -E '^[[:space:]]*PG_SUPER_PASSWORD[[:space:]]*=' "$PG_SECRET_FILE" 2>/dev/null | tail -n 1)"
    [ -n "$line" ] || return 1
    val="${line#*=}"
    # 去掉首尾空白和成对的引号
    val="$(printf '%s' "$val" | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//')"
    case "$val" in
        \'*\') val="${val#\'}"; val="${val%\'}" ;;
        \"*\") val="${val#\"}"; val="${val%\"}" ;;
    esac
    [ -n "$val" ] || return 1
    PG_SUPER_PASSWORD="$val"
    return 0
}

# 口令文件权限过宽就提醒；不打印内容。
pg_check_secret_perms() {
    [ -f "$PG_SECRET_FILE" ] || return 0
    local mode
    mode="$(stat -c '%a' "$PG_SECRET_FILE" 2>/dev/null)" || return 0
    case "$mode" in
        600 | 400) ;;
        *) warn "口令文件 ${PG_SECRET_FILE} 权限是 ${mode}，建议 chmod 600（只有 root 能读）" ;;
    esac
}

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

# 把口令里的单引号转义成 ''（SQL 字面量规则）。返回值仍然是明文，只经管道进入 psql，不打印。
pg_sql_quote() {
    printf '%s' "$1" | sed "s/'/''/g"
}

postgres_roles() {
    require_root
    pg_require_cluster
    postgres_assert_user

    pg_load_password || die "没有拿到超级用户口令。二选一：
  1) export PG_SUPER_PASSWORD='<口令>'  再用同一行运行本命令（前面加空格可避开 shell 历史）
  2) 把 PG_SUPER_PASSWORD='<口令>' 写进 ${PG_SECRET_FILE}（已被 .gitignore 覆盖），然后 chmod 600
口令不会打印，也不会写进日志。"
    pg_check_secret_perms

    local pw_sql role exists sql=""
    pw_sql="$(pg_sql_quote "$PG_SUPER_PASSWORD")"

    for role in $PG_SUPER_ROLES; do
        case "$role" in
            postgres) die "PG_SUPER_ROLES 里不要包含 postgres（它由 peer 认证管理）" ;;
            *[!a-z0-9_]*) die "角色名只能用 a-z 0-9 _: ${role}" ;;
        esac
    done

    for role in $PG_SUPER_ROLES; do
        # 先查再建：CREATE ROLE 不能放在 DO 块里，这样也更容易看清动作。
        exists="$(printf "SELECT 1 FROM pg_roles WHERE rolname = '%s';\n" "$role" | pg_admin_query | head -n 1)"
        if [ "$exists" = "1" ]; then
            sql="${sql}ALTER ROLE ${role} WITH LOGIN SUPERUSER CREATEDB CREATEROLE PASSWORD '${pw_sql}';
"
            log "角色 ${role} 已存在，对齐权限和口令"
        else
            sql="${sql}CREATE ROLE ${role} WITH LOGIN SUPERUSER CREATEDB CREATEROLE PASSWORD '${pw_sql}';
"
            log "创建角色 ${role}"
        fi
    done

    printf '%s' "$sql" | pg_admin_psql postgres \
        || die "设置超级用户失败（口令来自口令文件或环境变量，未显示）"

    for role in $PG_SUPER_ROLES; do
        log "超级用户 ${role} 已就绪: LOGIN SUPERUSER CREATEDB CREATEROLE（口令已更新，未显示）"
    done
    log "本地连接用 scram-sha-256 验证，和操作系统同名用户 ${PG_SUPER_ROLES} 不冲突（只有 postgres 走 peer）"
}

postgres_db() {
    require_root
    pg_require_cluster
    postgres_assert_user

    local owner="$PG_DB_OWNER" exists
    case "$owner" in
        '' | *[!a-z0-9_]*) die "PG_DB_OWNER 不合法: ${owner}" ;;
    esac
    case "$PG_DB" in
        '' | *[!a-zA-Z0-9_]*) die "PG_DB 不合法: ${PG_DB}" ;;
        [0-9]*) die "PG_DB 不能以数字开头: ${PG_DB}" ;;
    esac

    exists="$(printf "SELECT 1 FROM pg_database WHERE datname = '%s';\n" "$PG_DB" | pg_admin_query | head -n 1)"
    if [ "$exists" = "1" ]; then
        log "库 ${PG_DB} 已存在，只补齐 owner 和权限"
        printf 'ALTER DATABASE %s OWNER TO %s;\n' "$PG_DB" "$owner" | pg_admin_psql postgres \
            || die "修改库 ${PG_DB} 的 owner 失败"
    else
        printf 'CREATE DATABASE %s OWNER %s ENCODING %s;\n' "$PG_DB" "$owner" "UTF8" | pg_admin_psql postgres \
            || die "创建库 ${PG_DB} 失败"
        log "库 ${PG_DB} 已创建（owner ${owner}）"
    fi

    # 授权分三层，缺一层就会出现"超级用户能用、别人看不见"的情况：
    #   1) 库级：CONNECT / TEMP / CREATE
    #   2) schema 级：public schema 改成 owner，并对两个角色全权
    #   3) 默认权限：将来新建的表/序列/函数自动带权限（ALTER DEFAULT PRIVILEGES 只对指定角色生效，
    #      所以 sspacee 和 root 各设一遍）
    local roles_csv="" grant_sql
    for grant_sql in $PG_SUPER_ROLES; do
        roles_csv="${roles_csv:+${roles_csv},}${grant_sql}"
    done
    [ -n "$roles_csv" ] || die "PG_SUPER_ROLES 为空"

    {
        printf 'GRANT ALL PRIVILEGES ON DATABASE %s TO %s;\n' "$PG_DB" "$roles_csv"
        printf 'ALTER SCHEMA public OWNER TO %s;\n' "$owner"
        printf 'GRANT ALL PRIVILEGES ON SCHEMA public TO %s;\n' "$roles_csv"
        printf 'GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO %s;\n' "$roles_csv"
        printf 'GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO %s;\n' "$roles_csv"
        printf 'GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO %s;\n' "$roles_csv"
        for grant_sql in $PG_SUPER_ROLES; do
            printf 'ALTER DEFAULT PRIVILEGES FOR ROLE %s IN SCHEMA public GRANT ALL ON TABLES TO %s;\n' "$grant_sql" "$roles_csv"
            printf 'ALTER DEFAULT PRIVILEGES FOR ROLE %s IN SCHEMA public GRANT ALL ON SEQUENCES TO %s;\n' "$grant_sql" "$roles_csv"
            printf 'ALTER DEFAULT PRIVILEGES FOR ROLE %s IN SCHEMA public GRANT ALL ON FUNCTIONS TO %s;\n' "$grant_sql" "$roles_csv"
        done
    } | pg_admin_psql "$PG_DB" || die "库 ${PG_DB} 授权失败"

    log "库 ${PG_DB}: owner ${owner}，${roles_csv} 已获得库/schema/默认权限（新建对象自动可见）"
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
    for db in $PG_DB; do
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
