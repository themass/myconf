-- FreeRADIUS 3.2.x 需要、但旧库（2.1.12 时代）没有的表
--
-- 背景：
--   3.2.10 的 simul_count_query / simul_verify_query 里多了一个
--   `LEFT OUTER JOIN nasreload n USING (nasipaddress)`，用它在 NAS 重启后
--   把"重启前就挂着、但实际已断"的会话判为失效。
--   旧版 2.1.12 的这两个查询只查 radacct，没有这张表，所以迁移过来的库里也没有。
--
--   新机启用 session 段的 sql（和老机行为一致，用于 Simultaneous-Use 并发限制）后，
--   每次认证都会跑 simul_count_query，于是报：
--     ERROR 1146 (42S02): Table 'radius.nasreload' doesn't exist
--   并发检查随之失效。
--
-- 解决：把官方 schema.sql 里的定义补进来。表是空的即可，reloadtime 由
-- accounting-on 时写入。
--
-- 由 bash infra.sh radius 幂等执行（CREATE TABLE IF NOT EXISTS）。

CREATE TABLE IF NOT EXISTS nasreload (
  nasipaddress varchar(15) NOT NULL,
  reloadtime   datetime    NOT NULL,
  PRIMARY KEY (nasipaddress)
) ENGINE = INNODB DEFAULT CHARSET = utf8mb3;
