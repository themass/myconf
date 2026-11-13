-- FreeRADIUS 3.2.x 需要、但旧库（2.1.12 / daloRADIUS 时代）没有的表和列
--
-- 背景：
--   迁移过来的 radius 库是 2.1.12 + daloRADIUS 的结构，和 3.2.10 官方
--   mods-config/sql/main/mysql/schema.sql 对不上。两处会直接让功能失效：
--
--   1) nasreload 表不存在
--      3.2.10 的 simul_count_query / simul_verify_query 多了
--      `LEFT OUTER JOIN nasreload n USING (nasipaddress)`，用它把 NAS 重启后
--      实际已断的会话判为失效。老版这两个查询只查 radacct。
--      缺表 → 每次认证报 ERROR 1146，Simultaneous-Use 并发检查静默失效。
--
--   2) radacct 缺 6 个计费列
--      3.2.10 的 accounting column_list 会写 acctupdatetime / acctinterval /
--      framedipv6address / framedipv6prefix / framedinterfaceid /
--      delegatedipv6prefix。老结构是 daloRADIUS 的
--      (groupname, acctstartdelay, acctstopdelay, xascendsessionsvrkey,
--       fromAddr, toAddr, status)。
--      缺列 → 每条 Accounting-Request 都报 Unknown column，计费全丢。
--      注意这里是**加列**，不是重建表：老列的语义和质量仍在，只是 3.2 不再写它们。
--      （迁移后 radacct 是 0 行，加列不涉及数据回填。）
--
--   老库多出来的列保留不动：daloRADIUS 的 Web 界面还在读它们。
--
-- 幂等：表用 CREATE TABLE IF NOT EXISTS；列用 information_schema 判断后
-- ALTER，MySQL 8.0 的 ADD COLUMN 没有 IF NOT EXISTS。
-- 由 bash infra.sh radius 执行。

CREATE TABLE IF NOT EXISTS nasreload (
  nasipaddress varchar(15) NOT NULL,
  reloadtime   datetime    NOT NULL,
  PRIMARY KEY (nasipaddress)
) ENGINE = INNODB DEFAULT CHARSET = utf8mb3 COLLATE = utf8mb3_unicode_ci;

-- 已经存在但 collation 不对的库要就地改正。
--
-- 第一版建表时没写 COLLATE，nasreload 继承了服务端的 utf8mb3_general_ci，
-- 而 radacct.nasipaddress 是 utf8mb3_unicode_ci。simul_count_query 里
--   LEFT OUTER JOIN nasreload n USING (nasipaddress)
-- 两列 collation 不一致，MySQL 8.0 直接报
--   ERROR 1267 (HY000): Illegal mix of collations
--   (utf8mb3_unicode_ci,IMPLICIT) and (utf8mb3_general_ci,IMPLICIT)
-- 每次认证都失败。
ALTER TABLE nasreload CONVERT TO CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci;

DROP PROCEDURE IF EXISTS radius_add_missing_columns;

DELIMITER //
CREATE PROCEDURE radius_add_missing_columns()
BEGIN
  -- radacct：3.2.x 计费写入用到的列
  IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                 WHERE table_schema = DATABASE() AND table_name = 'radacct'
                   AND column_name = 'acctupdatetime') THEN
    ALTER TABLE radacct ADD COLUMN acctupdatetime datetime NULL DEFAULT NULL AFTER acctstarttime;
  END IF;

  IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                 WHERE table_schema = DATABASE() AND table_name = 'radacct'
                   AND column_name = 'acctinterval') THEN
    ALTER TABLE radacct ADD COLUMN acctinterval int(12) DEFAULT NULL AFTER acctstoptime;
  END IF;

  IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                 WHERE table_schema = DATABASE() AND table_name = 'radacct'
                   AND column_name = 'framedipv6address') THEN
    ALTER TABLE radacct ADD COLUMN framedipv6address varchar(45) NOT NULL DEFAULT '' AFTER framedipaddress;
  END IF;

  IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                 WHERE table_schema = DATABASE() AND table_name = 'radacct'
                   AND column_name = 'framedipv6prefix') THEN
    ALTER TABLE radacct ADD COLUMN framedipv6prefix varchar(45) NOT NULL DEFAULT '' AFTER framedipv6address;
  END IF;

  IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                 WHERE table_schema = DATABASE() AND table_name = 'radacct'
                   AND column_name = 'framedinterfaceid') THEN
    ALTER TABLE radacct ADD COLUMN framedinterfaceid varchar(44) NOT NULL DEFAULT '' AFTER framedipv6prefix;
  END IF;

  IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                 WHERE table_schema = DATABASE() AND table_name = 'radacct'
                   AND column_name = 'delegatedipv6prefix') THEN
    ALTER TABLE radacct ADD COLUMN delegatedipv6prefix varchar(45) NOT NULL DEFAULT '' AFTER framedinterfaceid;
  END IF;

  IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                 WHERE table_schema = DATABASE() AND table_name = 'radacct'
                   AND column_name = 'class') THEN
    ALTER TABLE radacct ADD COLUMN class varchar(64) DEFAULT NULL;
  END IF;

  -- 官方 schema 给这些新列都建了索引，acctinterval / class 还有单独的 KEY。
  IF NOT EXISTS (SELECT 1 FROM information_schema.statistics
                 WHERE table_schema = DATABASE() AND table_name = 'radacct'
                   AND index_name = 'framedipv6address') THEN
    ALTER TABLE radacct ADD KEY framedipv6address (framedipv6address);
  END IF;

  IF NOT EXISTS (SELECT 1 FROM information_schema.statistics
                 WHERE table_schema = DATABASE() AND table_name = 'radacct'
                   AND index_name = 'framedipv6prefix') THEN
    ALTER TABLE radacct ADD KEY framedipv6prefix (framedipv6prefix);
  END IF;

  IF NOT EXISTS (SELECT 1 FROM information_schema.statistics
                 WHERE table_schema = DATABASE() AND table_name = 'radacct'
                   AND index_name = 'framedinterfaceid') THEN
    ALTER TABLE radacct ADD KEY framedinterfaceid (framedinterfaceid);
  END IF;

  IF NOT EXISTS (SELECT 1 FROM information_schema.statistics
                 WHERE table_schema = DATABASE() AND table_name = 'radacct'
                   AND index_name = 'delegatedipv6prefix') THEN
    ALTER TABLE radacct ADD KEY delegatedipv6prefix (delegatedipv6prefix);
  END IF;

  IF NOT EXISTS (SELECT 1 FROM information_schema.statistics
                 WHERE table_schema = DATABASE() AND table_name = 'radacct'
                   AND index_name = 'acctinterval') THEN
    ALTER TABLE radacct ADD KEY acctinterval (acctinterval);
  END IF;

  IF NOT EXISTS (SELECT 1 FROM information_schema.statistics
                 WHERE table_schema = DATABASE() AND table_name = 'radacct'
                   AND index_name = 'class') THEN
    ALTER TABLE radacct ADD KEY class (class);
  END IF;
END //
DELIMITER ;

CALL radius_add_missing_columns();
DROP PROCEDURE IF EXISTS radius_add_missing_columns;
