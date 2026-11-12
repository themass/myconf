#!/usr/bin/env bash
# 数据库账号初始化：建用户、设口令、授权。
#
#   bash dbinit.sh mysql [SQL文件]      默认 conf/mysql/init.sql
#   bash dbinit.sh postgres [SQL文件]   默认 conf/postgres/init.sql
#   bash dbinit.sh all                  两个都跑
#
# 和安装脚本分开的原因：账号和权限会变，安装不需要重跑。
#   - 装 MySQL：bash infra.sh mysql
#   - 装 PostgreSQL：bash vpn.sh postgres setup
#   - 改口令/加用户/调授权：改 conf/<db>/init.sql，再跑本脚本
#
# PostgreSQL 那段会先保证库存在（uher），因为 GRANT 依赖它。
#
# 所有 SQL 都是幂等的：重复执行结果一样，不会因为"用户已存在"中断。

if [ -z "${BASH_VERSION:-}" ]; then
    command -v bash >/dev/null 2>&1 && exec bash "$0" "$@"
    echo "需要 bash: bash $0 ..." >&2
    exit 2
fi

VPN_SHELL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export VPN_SHELL_DIR
# shellcheck source=lib/common.sh
source "${VPN_SHELL_DIR}/lib/common.sh"

PG_VERSION="${PG_VERSION:-17}"
PG_DB="${PG_DB:-uher}"
PG_DB_OWNER="${PG_DB_OWNER:-sspacee}"

dbinit_usage() {
    cat <<EOF
用法: bash dbinit.sh <mysql|postgres|all> [SQL文件]

  mysql     执行 conf/mysql/init.sql（建账号、设口令、授权）
  postgres  执行 conf/postgres/init.sql（建角色、建库 uher、授权）
  all       两个都执行

环境变量:
  PG_VERSION     PostgreSQL 版本，默认 ${PG_VERSION}
  PG_DB          业务库名，默认 ${PG_DB}
  PG_DB_OWNER    业务库 owner，默认 ${PG_DB_OWNER}

注意: SQL 文件里含明文口令，会进 git 历史。要求保密时把口令换成
      从 conf/<db>/.env 读取（脚本预留了接口，见 docs/postgres.md）。
EOF
}

# ------------------------------------------------------------------ MySQL

dbinit_mysql() {
    require_root
    local sql="${1:-${MYCONF_HOME}/conf/mysql/init.sql}" host port

    have mysql || die "没有 mysql 客户端。先装: bash infra.sh mysql"
    [ -f "$sql" ] || die "缺少 ${sql}"

    # root 只有 root@localhost 时，TCP 会被解析成 root@<主机名> 而拒绝，所以走 socket。
    # 口令从 .env 或环境变量来，避免把口令写进 SQL 文件的场景下也能跑。
    local pw="${MYSQL_APP_PASSWORD:-Themass@5296}"
    if [ -f "${MYCONF_HOME}/conf/mysql/.env" ]; then
        local line
        line="$(grep -E '^[[:space:]]*MYSQL_APP_PASSWORD[[:space:]]*=' "${MYCONF_HOME}/conf/mysql/.env" 2>/dev/null | tail -n 1)"
        if [ -n "$line" ]; then
            pw="${line#*=}"
            pw="$(printf '%s' "$pw" | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//' -e "s/^'//" -e "s/'$//" -e 's/^"//' -e 's/"$//')"
        fi
    fi

    log "执行 ${sql}（MySQL）"
    # init.sql 里已经写了口令，这里的 pw 只是用于 root 登录。
    if MYSQL_PWD="$pw" mysql --no-defaults -uroot <"$sql"; then
        log "MySQL 账号已初始化（口令未显示）"
    else
        die "MySQL 账号初始化失败。检查 ${sql} 和 root 的登录方式（本机 socket 是否可用）"
    fi
}

# ------------------------------------------------------------------ PostgreSQL

dbinit_postgres() {
    require_root
    local sql="${1:-${MYCONF_HOME}/conf/postgres/init.sql}"

    have psql || die "没有 psql 客户端。先装: bash vpn.sh postgres setup"
    [ -f "$sql" ] || die "缺少 ${sql}"

    # 集群信息：版本/名字从 pg_lsclusters 取，不写死。
    local ver name
    ver="$(pg_lsclusters --no-header 2>/dev/null | awk '$4=="online"{print $1; exit}')"
    [ -n "$ver" ] || ver="$(pg_lsclusters --no-header 2>/dev/null | awk 'NR==1{print $1}')"
    name="$(pg_lsclusters --no-header 2>/dev/null | awk 'NR==1{print $2}')"
    [ -n "$ver" ] && [ -n "$name" ] || die "没有发现 PostgreSQL 集群。先装: bash vpn.sh postgres setup"

    if ! su -s /bin/sh postgres -c "pg_isready -q" 2>/dev/null; then
        die "PostgreSQL 没在运行。先启动: bash vpn.sh postgres start"
    fi

    # 库先存在，后面的 GRANT 才有意义。owner 给 PG_DB_OWNER。
    local exists
    exists="$(printf "SELECT 1 FROM pg_database WHERE datname = '%s';\n" "$PG_DB" \
        | su -s /bin/sh postgres -c "psql -tAq -d postgres -f -" | head -n 1)"
    if [ "$exists" = "1" ]; then
        log "库 ${PG_DB} 已存在"
    else
        log "创建库 ${PG_DB}（owner ${PG_DB_OWNER}）"
        # owner 可能还没建，先建角色再建库：init.sql 里有 CREATE ROLE，
        # 但库要在它之前存在。这里角色不存在就先建空的。
        printf "DO \$\$ BEGIN IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname='%s') THEN CREATE ROLE %s LOGIN; END IF; END \$\$;\n" \
            "$PG_DB_OWNER" "$PG_DB_OWNER" \
            | su -s /bin/sh postgres -c "psql -q -v ON_ERROR_STOP=1 -d postgres -f -" || die "创建角色 ${PG_DB_OWNER} 失败"
        printf 'CREATE DATABASE %s OWNER %s ENCODING UTF8;\n' "$PG_DB" "$PG_DB_OWNER" \
            | su -s /bin/sh postgres -c "psql -q -v ON_ERROR_STOP=1 -d postgres -f -" || die "创建库 ${PG_DB} 失败"
    fi

    log "执行 ${sql}（PostgreSQL ${ver}/${name}）"
    if su -s /bin/sh postgres -c "psql -q -v ON_ERROR_STOP=1 -d ${PG_DB} -f -" <"$sql"; then
        log "PostgreSQL 角色与授权已初始化（口令未显示）"
    else
        die "PostgreSQL 初始化失败。见上面的报错"
    fi
}

# ------------------------------------------------------------------ 入口

dbinit_main() {
    local action="${1:-}"
    [ $# -gt 0 ] && shift
    local file="${1:-}"
    [ $# -gt 0 ] && shift

    case "$action" in
        mysql) dbinit_mysql "$file" ;;
        postgres | pg) dbinit_postgres "$file" ;;
        all)
            dbinit_mysql "$file"
            dbinit_postgres "$file"
            ;;
        '' | help | -h | --help) dbinit_usage ;;
        *)
            err "未知目标: ${action}"
            dbinit_usage
            return 2
            ;;
    esac
}

dbinit_main "$@"
