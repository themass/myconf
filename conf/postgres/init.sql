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

-- ------------------------------------------------------------------ uher 库授权
-- 三层，缺一层就会出现"owner 能用、另一个账号看不到"：
--   1) 库级    2) schema 级    3) 默认权限（管将来新建的对象）
-- dbinit.sh 保证库存在后执行这一段。

GRANT ALL PRIVILEGES ON DATABASE uher TO root, sspacee;
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
