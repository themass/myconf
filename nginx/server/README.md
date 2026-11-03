# nginx 部署说明

## 文件与服务器路径对应

| 仓库文件 | 服务器路径 |
|---|---|
| `nginx/vpn.conf` | `/root/local/nginx/conf/server/vpn.conf`（替换原文件） |
| `book.conf` | `/root/local/nginx/conf/server/book.conf`（新增；book 的 443 用 Let's Encrypt 证书） |

注意：`book.ok123find.top` 只能在一个文件里定义。部署前先删掉服务器上 `sspacee3.conf` 里的 book 块和 `proxy/book.ok123find.top.conf`，否则会报 `conflicting server name`。

证书文件由 `ssl/` 下的脚本写入 `/root/local/nginx/conf/ssl/`。

上游 `vpn_server`、`chat_server`、`chat_server1`、`fetchurl_server`、`book_server` 需要在 nginx 的 `http {}` 里定义（当前 `upstream.conf` 只有 `vpn_server` 和 `php`，需要补全）。

## 步骤

1. 备份：`cp /root/local/nginx/conf/server/vpn.conf /root/local/nginx/conf/server/vpn.conf.bak`
2. 复制上表的文件到服务器对应路径
3. 申请证书（二选一）：
   - 正式：`bash ssl/certbot.sh 你的邮箱`
   - 测试：`bash ssl/self-signed.sh`（只用于测试，App 与 AdMob 不信任）
4. `/root/local/nginx/sbin/nginx -t` 通过后 `/root/local/nginx/sbin/nginx -s reload`
5. 验证：`curl -I https://api.ok123find.top/vvv/api/version.json`，返回 200 且没有 SSL 错误。
6. App 切到 HTTPS、确认用户都已更新后，打开 `vpn.conf` 里 80 端口的 301 跳转注释。
