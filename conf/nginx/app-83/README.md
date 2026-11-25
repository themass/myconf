# 8.217.122.83 上的 nginx（83 机）

本地编译 nginx 1.24.0，`/root/local/nginx-1.24.0`，配置在 `conf/server/`（`nginx.conf` 里
`include server/*.conf`，按文件名顺序加载）。这个目录是线上 `conf/server/` 的完整快照，
2026-11-26 整理成现在的样子。这台不走 `fleet.sh deploy nginx`（那是给 OpenResty 新机的），
改动都是直接改线上 + 同步到这里。

## 域名 → 文件 → 后端

| 域名 | 文件 | 后端 / 内容 |
|---|---|---|
| api.ok123find.top, file.ok123find.top, api.ok124find.top | vpn.conf | `vpn_server`（本机 :8888 主 + 104.160.191.19 备），路由见 api-routes.inc |
| api.sspacee.com, file.sspacee.com | api-sspacee.conf | 同上，完全镜像（含 game/companion/chat/metrics） |
| book.ok123find.top | book.conf | 静态 `/home/file/book/` |
| book.sspacee.com | book-sspacee.conf | 同上镜像 |
| game.ok123find.top | game.conf | H5 静态 `/home/web/webroot/plane-duel` + 游戏接口 `vpn_game` |
| game.sspacee.com | game-sspacee.conf | 同上镜像 |
| livekit.ok123find.top | livekit-ok123find.conf | 104.160.191.87:80（LiveKit 信令） |
| livekit.sspacee.com | livekit-sspacee.conf | 同上镜像 |
| ok123find.top, www.ok123find.top | zz-ok123find-proxy.conf | 反代 104.160.191.87（WordPress）；DNS 迁走后删 |
| （内部） | nginx_check.conf | `:9002/nginx_status`，只允许 127.0.0.1 |

`00-upgrade-map.conf` 定义 `$connection_upgrade`，所有 WebSocket（游戏 ws、livekit 信令）
都靠它；它必须在 server 块之前加载，所以文件名以 `00-` 开头。

## 共用路由：api-routes.inc

`vpn.conf` 与 `api-sspacee.conf` 两个 vhost 都 `include api-routes.inc;`（放在
`conf/api-routes.inc`，不匹配 `server/*.conf` 的通配，不会被自动加载）。
改路由只改这一份，两个域名域自动一致。里面是：公共代理头、ACME、`/v1/`（companion）、
`/metrics`（内网限定）、游戏两块、`/vvv/` 通用 API、chat 系列、BookManager、静态目录、首页。

## 游戏 WebSocket 的坑（两次踩中，别再改回去）

- location 里 `rewrite ... break` 写在 `proxy_pass` 前面时，location 级
  `proxy_set_header` 会被旁路，后端收到 `Host: <upstream 名>`、`Connection: close`，握手 400。
- 游戏两块用**带 URI 的 proxy_pass**（`http://vpn_game/api/game/ws`）做路径改写，
  并在块内显式 `Host 127.0.0.1:8888`、`Connection $connection_upgrade`。
- 游戏接口走 `vpn_game`（固定 127.0.0.1:8888），不走 `vpn_server` 多机池：
  远端 104.160.191.19 的 jar 没有 game 模块新版本，轮询会随机 404。

## 证书

| 组 | 路径 | 来源 |
|---|---|---|
| api/file/book.ok123find + api.ok124 | `/etc/letsencrypt/live/api.ok123find.top/`，renewal hook `nginx-reload.sh` 拷到 `conf/ssl/` | certbot（SAN 四个名字） |
| game.ok123find.top | hook `game-ok123.sh` 拷到 `conf/ssl/game-*.pem` | certbot |
| livekit.ok123find.top | vhost 直接引 `/etc/letsencrypt/live/livekit.ok123find.top/` | certbot |
| ok123find.top / www | `/etc/letsencrypt/live/ok123find.top/` | certbot |
| **sspacee 四个镜像** | `conf/ssl/{api,file/book,game,livekit}-sspacee-*.pem` | **现在是自签占位** |

sspacee 镜像的 A 记录还在 64.32.22.150（api.sspacee.com 已在 83）。DNS 改到 8.217.122.83 后逐组签发替换占位：

```bash
certbot certonly --webroot -w /var/www/letsencrypt \
  -d api.sspacee.com -d file.sspacee.com
cp -L /etc/letsencrypt/live/api.sspacee.com/fullchain.pem /root/local/nginx/conf/ssl/api-sspacee-fullchain.pem
cp -L /etc/letsencrypt/live/api.sspacee.com/privkey.pem  /root/local/nginx/conf/ssl/api-sspacee-privkey.pem
/root/local/nginx-1.24.0/sbin/nginx -s reload
```

book/game/livekit 同形（各自 `-d` 一个名字）。签发后把 vhost 里的 `conf/ssl/` 路径改指
`/etc/letsencrypt/live/<主名>/` 或加一个 deploy hook，跟 ok123find 组一致。

## 2026-11-26 清理掉的东西

备份在 83 机 `/root/bk-real.tgz` 和 `conf/backups-20261126/`：

- `openapi.conf`、`openapi-http.conf`：与 book.conf 同名冲突（`nginx -t` 一直在报的
  conflicting server name 就是它们），从未生效。删掉后警告消失。
- `sspacee.conf`、`sspacee3.conf`：sspacee.com 主域的旧 vhost，DNS 已指应用机，本地从不收到流量。
- `vpn.conf.bak*`、`vpn.conf.pre-*`、`upstream.conf.pre-*`：历史备份移出 server 目录。
- `conf/server` 曾是软链指向 `nginx-1.16.1/conf/server`（2024-03 留下的），已换成真目录；
  这就是之前 `tar`/`cp -a` 只打包出空目录的原因。
