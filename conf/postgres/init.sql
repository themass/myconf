-- PostgreSQL 角色与授权（唯一来源）
--
-- 用法：bash shell/dbinit.sh postgres
-- 这个文件只管角色和库级授权，不装 PostgreSQL（用 bash vpn.sh postgres setup）。
-- 整份可重复执行：存在就 ALTER，不存在才 CREATE。
--
-- 执行方式：以系统用户 postgres 走本机 socket（peer 认证），不需要输入口令。
-- 口令写在这里会进 git 历史；要求保密时改成由 dbinit.sh 从 conf/postgres/.env 读取。
--
-- 注意：库 uher 由 dbinit.sh 单独创建（CREATE DATABASE 不能放在这里，
-- 因为要处理"已存在"的情况）。这里只做 GRANT / ALTER DEFAULT PRIVILEGES。

-- ------------------------------------------------------------------ 角色
-- 两个管理账号，权限完全一致：LOGIN SUPERUSER CREATEDB CREATEROLE
-- 想收敛权限时改成 NOSUPERUSER，并把下面的 GRANT 留作显式授权。

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'root') THEN
        CREATE ROLE root LOGIN;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'sspacee') THEN
        CREATE ROLE sspacee LOGIN;
    END IF;
END
$$;

ALTER ROLE root WITH LOGIN SUPERUSER CREATEDB CREATEROLE PASSWORD 'Themass@5296';
ALTER ROLE sspacee WITH LOGIN SUPERUSER CREATEDB CREATEROLE PASSWORD 'Themass@5296';

-- ------------------------------------------------------------------ 库级授权
-- 这个文件对"当前连着的那个库"生效，所以 dbinit.sh 会对 PG_DBS 里的每个库各跑一遍。
-- 库名用 current_database() 取，不在 SQL 里写死，加库不用改这里。
--
-- 三层，缺一层就会出现"owner 能用、另一个账号看不到"：
--   1) 库级    2) schema 级    3) 默认权限（管将来新建的对象）

DO $$
DECLARE db text := current_database();
BEGIN
    EXECUTE format('GRANT ALL PRIVILEGES ON DATABASE %I TO root, sspacee', db);
    EXECUTE format('GRANT CONNECT, TEMPORARY ON DATABASE %I TO "vpn@server"', db);
END
$$;

ALTER SCHEMA public OWNER TO sspacee;
GRANT ALL PRIVILEGES ON SCHEMA public TO root, sspacee;
GRANT ALL PRIVILEGES ON ALL TABLES    IN SCHEMA public TO root, sspacee;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO root, sspacee;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO root, sspacee;

-- ALTER DEFAULT PRIVILEGES 只对"指定角色将来创建的对象"生效，
-- 所以两个账号各设一遍，否则一个人建的表另一个人看不见。
ALTER DEFAULT PRIVILEGES FOR ROLE root    IN SCHEMA public GRANT ALL ON TABLES    TO root, sspacee;
ALTER DEFAULT PRIVILEGES FOR ROLE root    IN SCHEMA public GRANT ALL ON SEQUENCES TO root, sspacee;
ALTER DEFAULT PRIVILEGES FOR ROLE root    IN SCHEMA public GRANT ALL ON FUNCTIONS TO root, sspacee;
ALTER DEFAULT PRIVILEGES FOR ROLE sspacee IN SCHEMA public GRANT ALL ON TABLES    TO root, sspacee;
ALTER DEFAULT PRIVILEGES FOR ROLE sspacee IN SCHEMA public GRANT ALL ON SEQUENCES TO root, sspacee;
ALTER DEFAULT PRIVILEGES FOR ROLE sspacee IN SCHEMA public GRANT ALL ON FUNCTIONS TO root, sspacee;

-- ------------------------------------------------------------------ 业务读写账号
-- vpn@server：应用侧账号，读写数据 + 建表（DDL），但不给删库/建库/建角色的权限。
-- 和 MySQL 里的 'vpn@server' 是两个独立的东西：那边是"用户 vpn 从主机 server"，
-- 这里整个字符串就是角色名。角色名含 @，所有地方都必须用双引号。
--
-- 权限说明：
--   * CREATE ON SCHEMA public —— 允许建表，这是应用做 migration 的前提。
--   * 表级 TRUNCATE 也给了，因为 migration 工具常用。
--   * 没给 NOSUPERUSER/NOCREATEDB/NOCREATEROLE，也拿不到别人的表。

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'vpn@server') THEN
        CREATE ROLE "vpn@server" LOGIN;
    END IF;
END
$$;

-- 显式写全属性，重复执行会把权限收回成"普通登录角色"。
ALTER ROLE "vpn@server" WITH LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE PASSWORD 'Themass@5296';

-- 库级：连接 + 建临时表
GRANT CONNECT, TEMPORARY ON DATABASE uher TO "vpn@server";

-- schema 级：USAGE 才能看见表，CREATE 才能建表
GRANT USAGE, CREATE ON SCHEMA public TO "vpn@server";

-- 现有对象
GRANT SELECT, INSERT, UPDATE, DELETE, TRUNCATE, REFERENCES, TRIGGER
    ON ALL TABLES IN SCHEMA public TO "vpn@server";
GRANT USAGE, SELECT, UPDATE ON ALL SEQUENCES IN SCHEMA public TO "vpn@server";
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO "vpn@server";

-- 将来由 root 或 sspacee 新建的表/序列也要自动带上权限，
-- 否则应用跑一段时间后会突然报 "permission denied for table xxx"。
ALTER DEFAULT PRIVILEGES FOR ROLE root    IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE, TRUNCATE, REFERENCES, TRIGGER ON TABLES TO "vpn@server";
ALTER DEFAULT PRIVILEGES FOR ROLE root    IN SCHEMA public GRANT USAGE, SELECT, UPDATE ON SEQUENCES TO "vpn@server";
ALTER DEFAULT PRIVILEGES FOR ROLE root    IN SCHEMA public GRANT EXECUTE ON FUNCTIONS TO "vpn@server";
ALTER DEFAULT PRIVILEGES FOR ROLE sspacee IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE, TRUNCATE, REFERENCES, TRIGGER ON TABLES TO "vpn@server";
ALTER DEFAULT PRIVILEGES FOR ROLE sspacee IN SCHEMA public GRANT USAGE, SELECT, UPDATE ON SEQUENCES TO "vpn@server";
ALTER DEFAULT PRIVILEGES FOR ROLE sspacee IN SCHEMA public GRANT EXECUTE ON FUNCTIONS TO "vpn@server";
