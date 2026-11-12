# VPN 服务端安装脚本

统一入口 `vpn.sh`，所有协议都是 `bash vpn.sh <模块> <动作>`。服务器公网地址、出口网卡、监听地址都由脚本自动识别，识别错了才需要手动指定。

```bash
bash vpn.sh help                  # 总览
bash vpn.sh <模块> help           # 某个模块的动作和环境变量
bash vpn.sh ports                 # 各协议默认端口 + 本机监听情况
bash vpn.sh links                 # 已安装协议的客户端链接
```

## 模块与默认端口

同一台机器上可以全部装上，默认端口互不冲突。

| 模块 | 协议 | 默认端口 | 改端口的环境变量 |
|---|---|---|---|
| `strongswan` | IKEv2/IPsec（strongSwan 6.x，swanctl + vici），地址池 10.0.0.0/24 | udp 8081 (IKE) / 8080 (NAT-T) | `SS_IKE_PORT` `SS_NATT_PORT` `IPSEC_SUBNET` |
| `xray` | VLESS + Reality | tcp 443 | `XRAY_PORT` |
| `singbox` | VLESS + Reality | tcp 444 | `SB_VLESS_PORT` |
| `singbox` | Trojan | tcp 8443 | `SB_TROJAN_PORT` |
| `singbox` | VMess + WebSocket | tcp 8880 | `SB_VMESS_PORT` |
| `singbox` | Shadowsocks | tcp+udp 8388 | `SB_SS_PORT` |
| `singbox` | Hysteria2 | udp 8444 | `SB_HY2_PORT` |
| `wireguard` | WireGuard（内网 10.66.0.0/16） | udp 51820 | `WG_PORT` |
| `ssr` | ShadowsocksR / ss-panel | 见 `conf/ssr/` | |
| `postgres` | PostgreSQL 17 的安装、启停、超级用户、业务库（说明见 `docs/postgres.md`） | tcp 5432（只监听内网） | `PG_VERSION` `PG_PORT` |
| `system` | 依赖、系统升级、内核参数、BBR、IPsec NAT、监控、诊断 | | |
| `health` | 运行状况总览和日志（只读） | | |

端口被其他进程占用时脚本会停下并说明占用者，不会覆盖。云厂商的安全组需要自己在控制台放行，脚本每次结束会列出要放行的端口。

## 常用流程

```bash
# Xray VLESS+Reality（装完直接输出客户端链接）
bash vpn.sh xray install

# sing-box：一次装全部协议，或者按需添加
bash vpn.sh singbox add all
bash vpn.sh singbox add hysteria2
bash vpn.sh singbox links

# WireGuard：App 设备的公钥由后端管理，服务器每分钟自动拉取（地址规划见 docs/WIREGUARD-BACKEND.md）
bash vpn.sh wireguard install
WG_SYNC_URL=https://api.example.com/vvv/api/noapp/wg/peers.txt WG_SYNC_TOKEN=<令牌> bash vpn.sh wireguard sync-install
bash vpn.sh wireguard add-peer laptop      # 自己电脑等手工 peer，地址落在保留段 10.66.255.0/24

# strongSwan 6.x 一键（编译 + 配置 + 证书 + 防火墙 + 内核参数）
bash vpn.sh strongswan all

# 升级系统包：先模拟，再执行。默认不换内核、不自动重启服务；full 才是 dist-upgrade
bash vpn.sh system upgrade dry-run
bash vpn.sh system upgrade

# 运行状况和日志（只读）：服务、端口、连接数、近期错误；日志默认打码 UUID 和密钥
bash vpn.sh health
bash vpn.sh health logs xray -f
```

## IKEv2 排障

**客户端连上后没有网，或者日志里没有连接记录**：先看 udp 端口是不是被别的 charon 占着，再看日志。

```bash
ss -lunp | grep -E ':(8080|8081) '            # 应该都是 charon
ps aux | grep '[c]haron'                       # 应该只有一个 charon-systemd
bash vpn.sh health logs strongswan -f          # 手机再连一次，看 IKE_SA 和 EAP/RADIUS 的日志
```

- 端口被占用或服务状态乱了：`bash vpn.sh strongswan clean force`，再 `bash vpn.sh strongswan config-port`（或 `config`）。
- 认证失败找 `EAP` 或 `RADIUS` 字样；RADIUS 的来源 IP 白名单见 `bash radius.sh status`。
- 客户端收到 `NO_PROPOSAL_CHOSEN`、服务器日志是 `no IKE config found`：连接配置没加载（`swanctl --list-conns` 为空）。服务启动时会自动加载；旧机器上的 systemd 单元没有这一步，运行 `bash vpn.sh strongswan config-port` 更新。
- 客户端认证通过后服务器整台失联：`swanctl.conf` 里有 `remote_ts = 0.0.0.0/0`，服务器自己的流量被送进了客户端隧道。用 `config-port` 重新生成配置（模板里已去掉）。

## 非 VPN 的基础服务（nginx、MySQL、PostgreSQL、FreeRADIUS、Redis、PHP、JDK）

```bash
bash infra.sh nginx      # OpenResty（官方 apt 源，最新版，自带常用模块）+ conf/nginx 站点配置
bash infra.sh redis      # Redis（apt），配置取自 conf/redis/redis.conf
bash infra.sh mysql      # MySQL 5.6.40（官方 tarball + systemd，版本固定，和线上一致）
bash infra.sh radius     # FreeRADIUS 3.2.x（NetworkRadius 官方 apt 源）+ sql 模块
bash infra.sh jdk        # OpenJDK 17 + Maven
bash infra.sh php        # PHP 8.4（sury 源）+ php-fpm 池 web（unix socket）+ composer
PG_ADMIN_PASSWORD='<口令>' bash infra.sh postgres   # PostgreSQL 17（PGDG 源），只听内网地址，全部 scram-sha-256

bash svc.sh status       # 所有基础服务的状态、自启、端口
bash svc.sh restart nginx
bash svc.sh logs mysql -f

bash radius.sh clients   # 用 conf/radius/clients.conf 替换线上的，校验通过才重启，失败自动还原
bash radius.sh debug     # 停掉 freeradius 前台调试（radiusd -X）
```

- 服务由 systemd 管理，不再 `pkill -9`；`infra.sh` 装的服务开机自启。
- `infra.sh` 的数据库连接参数取自 `conf/radius/sql.conf`，`clients.conf` 的共享密钥只在服务器上，不显示在日志里。
- `infra.sh` 里的 `innerip` 占位符自动换成本机内网地址；没有内网地址时只绑 127.0.0.1，需要的话设 `INFRA_BIND`。
- MySQL 5.6.40 和 Redis 6.0 都是老版本，MySQL 5.6 已停止维护。版本升级会影响线上数据和认证，没有单独测过，所以保持不变。

## PostgreSQL：安装、账号、业务库

安装和配置（`postgresql.conf` / `pg_hba.conf`）由 `infra.sh postgres` 负责；
装好之后还要建超级用户和业务库，用 `vpn.sh postgres`，两者不重复实现：

```bash
# 首次：装包 + 建超级用户 root/sspacee + 建库 uher 并授权（可重复运行）
read -rsp 'PG_SUPER_PASSWORD: ' PG_SUPER_PASSWORD; echo; export PG_SUPER_PASSWORD
bash vpn.sh postgres setup

# 只做其中一步
bash vpn.sh postgres install
bash vpn.sh postgres roles      # 角色存在就 ALTER 对齐权限和口令
bash vpn.sh postgres db         # 库/owner/schema/默认权限一次补齐

# 启停和自检
bash vpn.sh postgres status | start | stop | restart
bash vpn.sh postgres check
```

- 服务以系统用户 `postgres` 运行，数据目录 `/var/lib/postgresql/17/main` 只属于它（700）。
- 监听内网地址的 tcp 5432，`pg_hba.conf` 只允许本机 + 内网段，全部 `scram-sha-256`；只有 `local postgres` 走 peer。
- 超级用户 `root`、`sspacee`：`LOGIN SUPERUSER CREATEDB CREATEROLE`；库 `uher` owner 是 `sspacee`，
  两个账号都有库级 / schema 级 / 默认权限的完整权限（新建的表自动可见）。
- **口令不落盘到仓库**：脚本从 `PG_SUPER_PASSWORD` 或 `conf/postgres/.env`（`.gitignore` 覆盖，建议 `chmod 600`）
  读取，经 psql 标准输入传给服务器，不进命令行参数、不打印、不写日志。
- 运维细节（路径、认证、备份、故障处理）见 [docs/postgres.md](docs/postgres.md)。

## 旧脚本去哪了

| 旧脚本 | 现在 |
|---|---|
| `check.sh` | `system kernel-check` |
| `check_strongswan.sh` | `strongswan check` |
| `clean_strongswan_simple.sh` `cleanup_strongswan.sh` | `strongswan clean` |
| `force_clean_strongswan.sh` | `strongswan clean force` |
| `fix_strongswan_permissions.sh` | `strongswan clean`（重建目录和权限）+ `strongswan fix` |
| `test_minimal_strongswan.sh` | 删除：依赖的 `strongswan.conf.test` 早已不在仓库 |
| `vpn_setup_test.sh` | 删除：`vpn_setup.sh` 重构前的副本，写死了 IP，功能都在 `modules/` 里 |
| `soft_setup.sh` 的 `kernel` | `system bbr`（原来的 `setup_kernel` 只配置 BBR，下载内核的命令早就被注释掉了） |

被删的文件都在 git 历史里，取重构前的版本用 `git show 0bb0b0c9^:shell/<文件名>`。

注意：`strongswan clean` 之后规则和目录是重建的，防火墙规则由 `system iptables-ipsec` 管理，会自动装 `iptables-persistent`，重启后 NAT 不会丢。

## 仓库目录

```
myconf/
  shell/                   脚本（只放逻辑，配置全在 conf/）
    vpn.sh                 VPN 服务端统一入口（system strongswan xray singbox wireguard ssr health）
    infra.sh               非 VPN 基础软件安装（nginx、redis、mysql、radius、jdk、php）
    svc.sh                 非 VPN 服务的启停、状态、检查、日志
    radius.sh              FreeRADIUS 的 clients.conf 更新、启停、调试
    vpn_setup.sh           旧参数 -> vpn.sh 的转发（兼容旧手顺）
    ssvpn_setup.sh         同上
    lib/common.sh          日志、地址/网卡识别、模板渲染、端口检查、防火墙
    lib/xray_reality_fields.py   读 Xray 配置里的 Reality 字段
    modules/               每个模块一个文件
    docs/postgres.md       PostgreSQL 运维说明（安装位置、账号、库、备份、排障）
  conf/                    所有配置文件，按服务分目录
    system/                内核参数、limits、fail2ban jail、rc.local
    xray/  singbox/  wireguard/
    strongswan/
      6/                   strongSwan 6.x，swanctl 版（唯一支持的版本）
      strongswan.service   6.x 的 systemd 模板
    mysql/                 my.cnf、建表/数据 SQL、mysql.service
    redis/                 redis.conf
    radius/                clients.conf、sql.conf、建表 SQL；legacy-2.x/ 是旧版 2.x 的配置（先留着）
    php/                   php 通用设置 99-vpn.ini、php-fpm 池 web-pool.conf
    nginx/                 VPN 用的站点配置
    ssr/                   SSR 配置和 ss-panel 的 env
  python/                  Python 代码（不动，已纳入仓库）
  venv/                    Python 虚拟环境（不进仓库，见 .gitignore）
```

约定：配置文件里需要按机器变化的值用 `{{KEY}}` 占位，脚本渲染时填入；`conf/` 下的其它文件原样复制。

## 配置模板怎么用

模板用 `{{KEY}}` 占位。脚本渲染时把值填进去，**渲染后还有没填的占位符就直接报错**，不会把半成品配置写到服务器上。想改配置结构，改 `conf/` 下对应文件即可，不用动脚本。

- sing-box 每个协议一个 JSON，装在 `/etc/sing-box/conf.d/`，用 `-C` 目录方式合并加载；写入前会把整套配置放进临时目录用 `sing-box check` 校验，通过才生效。
- 每个协议的 UUID、密钥、密码保存在 `/etc/sing-box/state/<协议>.env`（root 才能读）。重复运行沿用，已经发出去的链接不会失效；`SB_FORCE=1` 才重新生成。
- Trojan / Hysteria2 默认生成以服务器 IP 为 SAN 的自签证书，链接里带 `insecure=1`。有域名和正式证书时：`SB_DOMAIN=example.com SB_CERT_FILE=... SB_KEY_FILE=... bash vpn.sh singbox add trojan`，注意证书私钥要让 `sing-box` 用户可读。

## 安装方式说明

- **Xray 版本固定 26.3.27，不要随便升级**：App 的 VLESS 客户端是 sing-box 1.13.5，Xray 26.7.28 及以后的 REALITY 服务端不接受它（服务端日志 `REALITY: processed invalid connection`，客户端 `reality verification failed`）。已经装了新版本的机器：`XRAY_VERSION=26.3.27 bash vpn.sh xray upgrade`，配置不动。

- **sing-box**：下载 GitHub 发布包，版本固定在 `SB_VERSION`（默认 1.13.5，和 App 里的 libbox 一致）。
- **Xray**：下载固定版本发布包，用 `.dgst` 里的 SHA256 校验通过后才安装；不执行任何远端脚本。服务器上已经用官方脚本装过 Xray 时，二进制和 systemd 服务保持原样，只管理配置。
- **系统参数**：内核参数写入 `/etc/sysctl.d/`，文件句柄数写入 `/etc/security/limits.d/`，重复运行不会堆叠。防火墙规则先检查再追加。

## 还没处理的

- `conf/radius/legacy-2.x/`：旧版 2.x 的配置，3.x 用不上，先留着。线上如果还在用其中某个功能（如拨号池、按次数限制），需要移植到 3.x。
- `mysql/Dump` 已移出仓库，见 `/Users/gqli/work/backup/`；仓库历史已改写，要在 GitHub 上生效需要强制推送。
