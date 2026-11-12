# PostgreSQL 运维说明

写给接手的人：这份文档回答"装在哪、谁在跑、怎么启停、有哪些账号和库、出事看哪里、怎么备份"。
不记录安装当天的排障过程。脚本是唯一事实来源，文档与脚本不一致时以脚本为准，并请顺手修文档。

对应脚本：

| 文件 | 作用 |
|---|---|
| `shell/modules/postgres.sh` | `vpn.sh postgres` 模块：启停、超级用户、业务库、自检 |
| `shell/infra.sh` 的 `postgres` 分支 | 装包、`postgresql.conf`/`pg_hba.conf` 的唯一来源 |
| `conf/postgres/postgresql.conf` | 服务端参数模板（渲染到 `conf.d/90-vpn.conf`） |
| `conf/postgres/pg_hba.conf` | 客户端认证模板（整份替换） |
| `conf/postgres/.env.example` | 口令文件模板；真实口令写在 `.env`（不进 git） |

---

## 1. 安装形态

- **软件包**：官方 PGDG apt 源（签名验证过）安装 `postgresql-17` + `postgresql-client-17`。
  Ubuntu 22.04 (jammy) 自带 14，所以走 PGDG；版本由 `PG_VERSION` 控制，默认 17。
- **集群**：Debian 的包管理方式，一个版本一个 cluster，名字 `main`。
  实际路径都带版本号，升级大版本会新增 `postgresql/<新版本>/main`，旧集群保留。
- **安装入口**：

  ```bash
  bash vpn.sh postgres install     # 只装包和配置（内部调用 infra.sh postgres）
  bash vpn.sh postgres setup       # 装包 + 建超级用户 + 建库（首次用这个）
  ```

  已经装过 PostgreSQL 的机器，`install` 会检测到集群并跳过装包，只做校验。

## 2. 路径

| 内容 | 路径 |
|---|---|
| 配置文件目录 | `/etc/postgresql/<版本>/main/` |
| 主配置 | `/etc/postgresql/<版本>/main/postgresql.conf`（包自带，**不要改**） |
| 本项目追加的参数 | `/etc/postgresql/<版本>/main/conf.d/90-vpn.conf` |
| 客户端认证 | `/etc/postgresql/<版本>/main/pg_hba.conf` |
| 数据目录 | `/var/lib/postgresql/<版本>/main/` |
| 运行日志 | `/var/log/postgresql/postgresql-YYYY-MM-DD.log` |
| 二进制 | `/usr/lib/postgresql/<版本>/bin/`（`psql` 等在 `/usr/bin`） |

版本默认 17，所以实际路径是 `/etc/postgresql/17/main/`、`/var/lib/postgresql/17/main/`。
**所有操作都要带上正确的版本号**，机器上只有一套集群时脚本会自动识别。

## 3. 运行用户与权限

- PostgreSQL 服务进程以**系统用户 `postgres`** 运行（Debian 包自动创建，`/usr/sbin/nologin`），
  不是 root，也不是业务账号。
- **数据目录只属于 `postgres`，权限 700**。`bash vpn.sh postgres check` 会核对 owner 和权限；
  `install` 发现 owner 不对会直接停下并给出 `chown` 命令，不会擅自改数据目录。
- 系统里如果另外有叫 `root`、`sspacee` 的**操作系统**用户，和数据库里的同名 role 没有关系：
  `pg_hba.conf` 里只有 `local ... postgres` 走 `peer`（即"系统用户 postgres 免密登录"），
  其余所有连接（包括同名的 root/sspacee）一律 `scram-sha-256` 口令认证。

## 4. 监听与认证

- **端口**：`5432`（`PG_PORT`）。改端口会同时改 `conf.d/90-vpn.conf`，脚本渲染时不写死。
- **监听地址**：默认是本机内网地址（取自 `INFRA_BIND` 或自动识别的第一块内网网卡）；
  没有内网地址时只监听 `127.0.0.1`。**不监听 0.0.0.0**，公网访问不成立。
- **认证方式**（`pg_hba.conf`，从严格到宽松）：

  | 来源 | 用户 | 方式 |
  |---|---|---|
  | 本机 unix socket | `postgres` | `peer` |
  | 本机 unix socket | 其他 | `scram-sha-256` |
  | `127.0.0.1/32`、`::1/128` | 全部 | `scram-sha-256` |
  | 本机内网地址所在 `/24` | 全部 | `scram-sha-256` |

  全部是口令认证，没有 `trust`。要加别的网段，改 `conf/postgres/pg_hba.conf` 的 `{{NET}}` 机制不够用，
  直接在模板末尾加一行 `host all all <网段> scram-sha-256`，再跑一次
  `bash infra.sh postgres`（会备份旧文件再覆盖）。
- 改完认证或参数：`bash vpn.sh postgres restart`。`pg_hba.conf` 也可以用 `SELECT pg_reload_conf();` 热加载，
  但参数改动需要重启。

## 5. 账号清单

| 角色 | 权限 | 用途 |
|---|---|---|
| `postgres` | 超级用户，系统内置 | 只通过本机 `peer` 认证使用；日常运维入口，不要给业务用 |
| `root` | `LOGIN SUPERUSER CREATEDB CREATEROLE` | 管理账号之一，与系统 root 同名但互不相干 |
| `sspacee` | `LOGIN SUPERUSER CREATEDB CREATEROLE` | 管理账号之一，也是业务库 owner |

- 两个管理账号由 `bash vpn.sh postgres roles` 创建或对齐。**重复运行安全**：存在就 `ALTER` 权限和口令，
  不存在才 `CREATE`。
- 两个账号的权限完全一致；之所以建两个，是历史习惯（root 用于个人运维，sspacee 用于应用侧）。
  真要收敛权限时改成 `CREATEDB` 即可，改 `PG_SUPER_ROLES` 之外的代码不用动。
- 口令：**仓库里没有，`git log` 里也没有**。脚本只从下面两处读，读不到就报错退出：
  1. 环境变量 `PG_SUPER_PASSWORD`（本次命令有效）；
  2. `conf/postgres/.env` 里的 `PG_SUPER_PASSWORD='...'`（已被 `.gitignore` 覆盖，`chmod 600`）。

  口令经标准输入传给 `psql`，不进命令行参数（`ps` 看不到）、不写日志、不打印。
  **不要**用 `PG_SUPER_PASSWORD=... bash vpn.sh postgres roles` 这种写法，它会留在 shell 历史里；
  先 `export`（前面加一个空格可避开 zsh/bash 历史），或者用口令文件。

- 新增其他管理账号：改 `PG_SUPER_ROLES="root sspacee 别人" bash vpn.sh postgres roles`，
  口令共用同一个变量。生产上建议给不同人不同账号，这属于后续演进。

## 6. 数据库清单

| 库 | owner | 授权 |
|---|---|---|
| `postgres` | `postgres` | 系统默认库，别删 |
| `template0` / `template1` | `postgres` | 建库模板，别动 |
| `uher` | `sspacee` | `root` 与 `sspacee` 均有库级、schema 级、默认权限的完整权限 |

`uher` 的授权分三层，少一层就会出现"owner 能用、另一个账号看不到"：

1. **库级**：`GRANT ALL PRIVILEGES ON DATABASE uher`（连接、临时表、建 schema）。
2. **schema 级**：`public` schema 的 owner 设成 `sspacee`，两个账号都 `GRANT ALL ON SCHEMA public`。
3. **默认权限**：对 `sspacee` 和 `root` 分别 `ALTER DEFAULT PRIVILEGES ... GRANT ALL ON TABLES/SEQUENCES/FUNCTIONS`。
   这一条管的是"将来谁新建的表"，没有它，`root` 建的表 `sspacee` 就看不见。

已有对象也会补一次 `GRANT ALL ON ALL TABLES/SEQUENCES/FUNCTIONS IN SCHEMA public`，
所以对已经跑起来一段时间的库重跑 `bash vpn.sh postgres db` 同样有效。

**注意**：`ALTER DEFAULT PRIVILEGES` 必须针对"未来创建对象的那个角色"分别设置。
目前脚本对 `PG_SUPER_ROLES` 里的每个角色都设了一遍，新增角色重跑 `db` 自动补上。
两个账号都是 SUPERUSER，实际上都能绕过权限检查；上面的授权是给"以后降权"留的余量，
也是给非超级用户账号（如果以后加）的正确做法。

## 7. 启停与状态

推荐用封装，参数风格和其它模块一致：

```bash
bash vpn.sh postgres status      # 集群、systemd 状态、端口监听、pg_isready
bash vpn.sh postgres start
bash vpn.sh postgres stop
bash vpn.sh postgres restart
bash vpn.sh postgres check       # 服务 + pg_hba + 角色 + 库 + 数据目录权限 + 磁盘
```

底层就是 Debian 的集群工具，出问题时可以直接用：

```bash
pg_lsclusters                                   # 看所有集群的版本/端口/状态
pg_ctlcluster 17 main restart                   # 启停指定集群
systemctl status postgresql@17-main             # 看 unit
journalctl -u postgresql@17-main -n 50 --no-pager
bash svc.sh status postgres                     # 和 MySQL/Redis 一起看
bash svc.sh logs postgres -f
```

- 服务单元是 `postgresql@17-main`，开机自启（`systemctl is-enabled` 应为 `enabled`）。
- `bash svc.sh stop postgres` 与 `bash vpn.sh postgres stop` 等价，两个入口都走 systemd，
  不存在 `pkill -9` 这种会把数据写坏的做法。
- 主机重启后如果没起来：先 `pg_lsclusters` 看状态，再看 `journalctl -u postgresql@17-main`。
  最常见的是磁盘满或数据目录权限被改过。

## 8. 日常检查

```bash
bash vpn.sh postgres check

# 手工看几个关键点
sudo -u postgres psql -c '\du'                  # 角色和权限
sudo -u postgres psql -c '\l'                   # 库和 owner
sudo -u postgres psql -d uher -c '\dn+'         # schema
psql "host=<内网IP> port=5432 user=sspacee dbname=uher"   # 验证口令认证可用
```

`\du` 里 `root` / `sspacee` 应为 `Superuser, Create role, Create DB`。
从别的机器连不上时，按顺序查：安全组/防火墙 → `listen_addresses` 是否为内网 IP →
`pg_hba.conf` 是否有对应网段 → 口令和密码加密方式（`password_encryption = scram-sha-256`）。

## 9. 备份建议

**最低要求：每天一次逻辑全量，保留 14 天，且至少复制到另一台机器。**

```bash
# 单库备份（压缩，-Fc 方便单表恢复）
sudo -u postgres pg_dump -Fc -d uher > /var/backups/pg/uher-$(date +%F).dump

# 全实例（含角色和权限，灾难恢复用）
sudo -u postgres pg_dumpall --globals-only > /var/backups/pg/globals-$(date +%F).sql
sudo -u postgres pg_dumpall > /var/backups/pg/all-$(date +%F).sql
```

- 备份目录 `/var/backups/pg` 要 `chmod 700`，文件属主 `postgres`；里面是明文数据，别放在 web 目录。
- 用 cron/systemd timer 跑，别手工记着。给 `sspacee` 账号备份时用
  `PGPASSWORD` 从环境变量给（同样不要写在命令行里）。
- 恢复单库：`sudo -u postgres createdb -O sspacee uher_restore && sudo -u postgres pg_restore -d uher_restore <file>`。
- **恢复演练每季度至少一次**：在另一台机器上恢复并 `SELECT count(*)` 对一下行数。
  没演练过的备份不算备份。
- 想做时间点恢复（PITR）需要另外开 `archive_mode` 和连续归档，属于后续工作；
  目前 `wal_level = replica`，只够流复制的前提条件，没有配归档。
- 大表且有停机窗口时用 `pg_basebackup` 做物理备份；日常不依赖它。

## 10. 常见故障

| 现象 | 先查 | 处理 |
|---|---|---|
| 服务起不来 | `journalctl -u postgresql@17-main -n 50` | 磁盘满、数据目录 owner 被改、端口被占 |
| 本机 `psql` 能进，远程连不上 | `ss -lntp \| grep 5432` | 只监听了 127.0.0.1 就检查 `INFRA_BIND` 和 `90-vpn.conf` |
| 提示 `no pg_hba.conf entry for host` | 客户端源 IP | `pg_hba.conf` 只放本机 + 内网 `/24` |
| 提示 `password authentication failed` | `\du`、口令来源 | 重跑 `bash vpn.sh postgres roles`（口令文件或环境变量是否就位） |
| 另一个账号看不到新建的表 | `\dp` | 重跑 `bash vpn.sh postgres db` 补默认权限 |
| 连接数满了 | `SELECT count(*) FROM pg_stat_activity;` | `max_connections` 在 `90-vpn.conf`，改完要重启 |
| 磁盘涨得快 | `du -sh /var/lib/postgresql/17/main` | 看 `log_min_duration_statement` 日志、WAL 大小、`pg_stat_user_tables` 的死元组 |

## 11. 不要做的事

- **不要改** `/etc/postgresql/17/main/postgresql.conf` 和 `pg_hba.conf` 里的 `90-vpn.conf` 之外内容：
  前者被包管理，后者是模板渲染出来的，下次跑脚本会被覆盖（旧文件会备份成 `.bak.<时间戳>`）。
  要改参数，改 `conf/postgres/postgresql.conf` 再重跑 `bash infra.sh postgres`。
- **不要把口令**写进脚本、README、提交信息、工单或聊天记录。要用就放 `conf/postgres/.env`，`chmod 600`。
- 不要用 `pkill -9 postgres`；要停就 `pg_ctlcluster 17 main stop` 或 `systemctl stop`。
- 不要删 `/var/lib/postgresql/17/main` 下的任何文件，`pg_ctlcluster` 会自己管。
- 大版本升级（17 → 18）不是改 `PG_VERSION` 重跑：需要新建集群 + `pg_upgrade`，单独安排窗口。
