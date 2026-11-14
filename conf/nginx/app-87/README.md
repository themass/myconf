# 应用机（104.160.191.87 / 64.32.22.150 等）的 nginx 配置

这台机器是**本地编译版 nginx 1.24.0**（`/root/local/nginx-1.24.0`，`/root/local/nginx` 是它的软链），
不是 `conf/nginx/` 那套 OpenResty 部署，`infra.sh nginx` 不会碰它。这里存的是它的线上配置快照，
方便追查和重建；改动请先在机器上改、`nginx -t` 通过、reload，再回存到本目录。

一块网卡上同时挂着 104.160.191.87、64.32.22.150、64.32.22.208、104.160.191.19、64.32.22.3，
对外域名全靠 `server_name` 区分。

| 文件 | 域名 | 说明 |
|---|---|---|
| `server/wp-ok123find.conf` | ok123find.top / www | WordPress，root `/home/web/webroot/wordpress`，PHP 走 `upstream php`（unix:/home/web/var/run/php.sock）；80 跳 https，443 用**自签**证书 `/root/local/sslkey/ok123find.top.{crt,key}`（SAN 含 www，10 年） |
| `server/sspacee-redirect.conf` | sspacee.com / www | 80 和 443 都 301 到 https://jc.sspacee.com，443 用 `sspacee.com` 自己的 Let's Encrypt 证书 |
| `server/jc-site-*.conf` | jc.sspacee.com | JobCome（Next.js 3001 / API 8000） |
| `server/newapi*.conf` | gpt.sspacee.com | New API |
| `server/openapi*.conf` | book.ok123find.top | 走 `/root/local/sslkey` 的自签证书 |
| `server/blog.conf.disabled` | sspacee.com | 旧的 WordPress 直连 vhost，已停用（重定向取代），保留备查 |

依赖：
- php-fpm 池 `[web]` → `/etc/php/7.4/fpm/pool.d/web.conf`，监听 `/home/web/var/run/php.sock`，属主 `web`
- systemd unit `/etc/systemd/system/nginx.service`（包装编译版 nginx，`ExecStartPre` 先 `nginx -t`）
- PHP 连的是远端 MySQL `mysql.sspacee.com:6666`（47.82.163.162）。RTT 约 172ms，一页 60+ 条查询
  要 13 秒左右；这是性能瓶颈，不是配置问题。
