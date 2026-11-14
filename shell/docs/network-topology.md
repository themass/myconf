# 网络拓扑

截止 2026-11-14，从各机器实测（`fleet.sh status` / `ss` / `nginx -T` / `dig`）整理，不是凭记忆。

## 一句话

一台应用机挂 5 个公网 IP 跑所有网站，一台阿里云机器跑数据库/缓存/RADIUS，一台老机器 8.217.122.83 兼做 book 站和 ok123find.top 的入口，另外 6 台散落在各机房的机器都是 VPN 节点。

## 域名层

| 域名 | 解析到 | 谁在服务 |
|---|---|---|
| sspacee.com / www | 64.32.22.150 | 应用机：301 → https://jc.sspacee.com |
| jc.sspacee.com | 64.32.22.150 | 应用机：JobCome（Next.js + API） |
| gpt.sspacee.com | 64.32.22.150 | 应用机：New API |
| ok123find.top / www | 8.217.122.83 | 8.217.122.83 反代 → 应用机 104.160.191.87 的 WordPress |
| book.ok123find.top | 8.217.122.83 | 8.217.122.83：openapi 反代 |
| api.ok123find.top / file.ok123find.top | 8.217.122.83 | 8.217.122.83：openapi 反代 |
| mysql.sspacee.com | 47.82.163.162 | 基础组件机：MySQL |
| radius.sspacee.com | 47.82.163.162 | 基础组件机：FreeRADIUS（VPN 节点靠它认证） |

DNS 在 DNSOwl（`ns1/2/3.dnsowl.com`）。

> ok123find.top 的站点其实跑在应用机上，只是 DNS 还指着 8.217.122.83，所以那台做了一层反代。
> 哪天把 A 记录改到 64.32.22.150，8.217.122.83 上的 `acme-ok123find.conf` 就可以删掉。

## 机器

### 应用机 — 一块网卡 5 个公网 IP

`104.160.191.87`、`64.32.22.150`、`64.32.22.208`、`104.160.191.19`、`64.32.22.3`
（同一 machine-id，全部在 ens3 上；任何"某台机器连不上"的判断都要先想到这一点）

- 本地编译版 nginx 1.24.0，`/root/local/nginx-1.24.0`，配置快照见 `conf/nginx/app-87/`
- systemd unit `nginx.service`（本仓库补的，`ExecStartPre` 先 `nginx -t`）
- PHP 7.4 + php-fpm 池 `[web]` → `/home/web/var/run/php.sock`
- 跑的站点：
  - `jc.sspacee.com` — JobCome：Next.js `:3001`、API `:8000`
  - `gpt.sspacee.com` — New API `:3000`
  - `ok123find.top` — WordPress（`/home/web/webroot/wordpress`），HTTPS 用 Let's Encrypt 证书
  - `book.ok123find.top` — openapi 反代
  - `sspacee.com` — 只做跳转，301 到 jc
- 其它监听：`:8081`、`:8082`（python）、`:2000`（v2ray）、`:8888`、`:9002`
- **性能瓶颈**：WordPress 的 MySQL 在 47.82.163.162，RTT 172ms，一页 60+ 查询要 13–15 秒

### 基础组件机 — 47.82.163.162（SSH 22）

| 服务 | 端口 | 备注 |
|---|---|---|
| MySQL 8.0 | 6666 | 库：`wordpress`、`sspanel`、`vpn`、`radius`、`test` |
| PostgreSQL | 5432 | |
| Redis | 6380 | 只监听内网 172.17.31.6 |
| FreeRADIUS 3.2.10 | udp 1812/1813 | 21 个 NAS 客户端，`conf/radius/clients.conf` |
| OpenResty | 80/443 | 静态文件 `/home/file/html`，`:80` 返回 403 |

`mysql.sspacee.com` 和 `radius.sspacee.com` 都指这里。这台机器的 RAM 上跑着 pmcd/pmlogger（4330、44321）。

### 老 nginx 机 — 8.217.122.83

- 本地编译 nginx，配置在 `/root/local/nginx-1.24.0/conf/server/`
- `book.ok123find.top`、`api/file.ok123find.top`、`sspacee.com`（配置还在，但 DNS 已不指这里）
- ok123find.top 的 **反向代理入口**（当前 DNS 指向，等 DNS 迁移后可撤）
- 另有 `:8888` java 服务、`:8388` ss-server、`:9002` 本机 nginx_check
- 上面有 certbot，ok123find.top 的证书就是在这里签的
- 是一台 VPN 节点（登录服务也在这台）

### VPN 节点

| 机器 | SSH | 跑的东西 |
|---|---|---|
| 38.78.147.253 | 17966 | strongSwan（IKE 8081 / NAT-T 8080）、xray `:2096`、sing-box（8388/8443/8880）、WireGuard `wg0` 10.66.0.1/16 |
| 103.115.18.229 | 22 | strongSwan（charon 跑在 8080/8081） |
| 43.110.45.118 | 22 | xray `:443` |
| 8.217.122.83 | 22 | 见上，同时是节点 |
| 91.149.239.221 | 22 | vvv-link java `:8888`（登录服务），**SSH 时通时不通** |
| 64.32.22.208 | 22 | 就是应用机（同一台的另一个 IP） |
| 104.160.191.19 | — | 就是应用机（同一台的另一个 IP） |

所有节点的 RADIUS 客户端指向 `radius.sspacee.com:1812`，共享密钥在 `conf/radius/clients.conf`。

### 应用服务 — 104.160.191.87

- JobCome（agent）、New API、companion agent，web 根在 `/home/web/webroot/{job-come,new-api,companion-agent,testserverV,wordpress}`

## 已知问题

1. **WordPress 慢**（13–15 秒/页）：跨机房 MySQL RTT 172ms × 60 条查询。要么迁本地 MySQL，要么上 Redis 对象缓存。
2. **ok123find.top 的证书续期**：目前由 8.217.122.83 上的 certbot 签、手工拷到应用机。DNS 改指应用机后，应在应用机上按 sspacee.com 同样的 webroot 方式续。
3. **91.149.239.221 SSH 不稳定**：多次出现连接超时，`fleet.sh` 对它的操作需要重试。
4. **应用机重启后**：nginx 和 php7.4-fpm 都已 enable，会自己起来。
5. **ok123find.com 没注册**（whois 无记录），不能配域名。

## 管理入口

```bash
cd shell
bash fleet.sh hosts        # 清单
bash fleet.sh status       # 各机服务 + 仓库版本
bash fleet.sh vpn restart  # 逐台重启 VPN
bash fleet.sh radius add-ip <ip>
```

机器清单在仓库根的 `.env`（不进 git）。
