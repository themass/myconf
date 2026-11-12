-- MySQL 8.0 账号与授权（唯一来源）
--
-- 用法：bash shell/dbinit.sh mysql
-- 这个文件只管账号，不建库。装 MySQL 用 bash infra.sh mysql。
--
-- 设计：整份是可重复执行的"声明式"定义 —— 跑一遍就是这个状态。
--   * 账号用 CREATE USER IF NOT EXISTS + ALTER USER，存在就改密码，不存在才建。
--   * 不需要的账号显式 DROP，重复执行不会留下历史残留。
--   * 8.0 已移除 GRANT ... IDENTIFIED BY，必须拆成 CREATE USER + GRANT。
--
-- 口令：写在这里方便直接部署，但会进 git 历史。要求保密时改成
-- 由 dbinit.sh 从 conf/mysql/.env 读取并替换 {{MYSQL_APP_PASSWORD}}。
--
-- 修改后同步跑一次 bash shell/dbinit.sh mysql，不要只改服务器。

-- ------------------------------------------------------------------ 清理

-- book 账号已废弃（本机没有 book_manager 库），保留定义会让授权悬空。
DROP USER IF EXISTS 'book'@'%';

-- ------------------------------------------------------------------ root
-- localhost 走本机连接；% 供外网工具使用。
-- 注意：root@'%' 在老库里只有 5 个库的权限，这里保持原样，不给 *.*。

CREATE USER IF NOT EXISTS 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'Themass@5296';
ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'Themass@5296';

CREATE USER IF NOT EXISTS 'root'@'127.0.0.1' IDENTIFIED WITH mysql_native_password BY 'Themass@5296';
ALTER USER 'root'@'127.0.0.1' IDENTIFIED WITH mysql_native_password BY 'Themass@5296';
GRANT ALL PRIVILEGES ON *.* TO 'root'@'127.0.0.1' WITH GRANT OPTION;

CREATE USER IF NOT EXISTS 'root'@'::1' IDENTIFIED WITH mysql_native_password BY 'Themass@5296';
ALTER USER 'root'@'::1' IDENTIFIED WITH mysql_native_password BY 'Themass@5296';
GRANT ALL PRIVILEGES ON *.* TO 'root'@'::1' WITH GRANT OPTION;

CREATE USER IF NOT EXISTS 'root'@'%' IDENTIFIED WITH mysql_native_password BY 'Themass@5296';
ALTER USER 'root'@'%' IDENTIFIED WITH mysql_native_password BY 'Themass@5296';
GRANT ALL PRIVILEGES ON `vpn`.*       TO 'root'@'%';
GRANT ALL PRIVILEGES ON `radius`.*    TO 'root'@'%';
GRANT ALL PRIVILEGES ON `sspanel`.*   TO 'root'@'%';
GRANT ALL PRIVILEGES ON `wordpress`.* TO 'root'@'%';

-- ------------------------------------------------------------------ 业务账号

CREATE USER IF NOT EXISTS 'vpn'@'%' IDENTIFIED WITH mysql_native_password BY 'Themass@5296';
ALTER USER 'vpn'@'%' IDENTIFIED WITH mysql_native_password BY 'Themass@5296';
GRANT ALL PRIVILEGES ON `vpn`.* TO 'vpn'@'%';

-- 用户名本身含 @，主机会是 %。拆解逻辑见 dbinit.sh。
CREATE USER IF NOT EXISTS 'vpn@server'@'%' IDENTIFIED WITH mysql_native_password BY 'Themass@5296';
ALTER USER 'vpn@server'@'%' IDENTIFIED WITH mysql_native_password BY 'Themass@5296';
GRANT ALL PRIVILEGES ON `vpn`.*       TO 'vpn@server'@'%';
GRANT ALL PRIVILEGES ON `radius`.*    TO 'vpn@server'@'%';
GRANT ALL PRIVILEGES ON `sspanel`.*   TO 'vpn@server'@'%';
GRANT ALL PRIVILEGES ON `wordpress`.* TO 'vpn@server'@'%';

CREATE USER IF NOT EXISTS 'radius'@'%' IDENTIFIED WITH mysql_native_password BY 'Themass@5296';
ALTER USER 'radius'@'%' IDENTIFIED WITH mysql_native_password BY 'Themass@5296';
GRANT ALL PRIVILEGES ON `radius`.* TO 'radius'@'%';

-- 老库遗留账号，明文口令未知，沿用原密码哈希（客户端不用改）。
-- 要统一成新口令：把下面两行换成 IDENTIFIED WITH mysql_native_password BY '新口令'。
CREATE USER IF NOT EXISTS 'mysspanel_free'@'%' IDENTIFIED WITH mysql_native_password AS '*DD8ABCF530A719D6EA86F71B29EC45DCAAEAFB69';
GRANT ALL PRIVILEGES ON `sspanel`.* TO 'mysspanel_free'@'%';

FLUSH PRIVILEGES;
