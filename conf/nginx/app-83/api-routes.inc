# api.ok123find.top / file.ok123find.top / api.ok124find.top 与
# api.sspacee.com / file.sspacee.com 两个 vhost 共用的路由（server 级）。
# 用绝对路径 include，不在 server/*.conf 通配范围内，不会被自动加载。
# 改路由只改这一份；域名差异（listen/server_name/证书）在各 vhost 文件里。

    client_max_body_size 20m;
    gzip on;
    gzip_types application/json text/plain text/css application/javascript;
    gzip_min_length 1024;

    # 代理公共头：后端需要真实 IP 与协议。
    # Connection 用 $connection_upgrade（00-upgrade-map.conf 定义）：
    # 普通请求为 "" 保持上游长连接，带 Upgrade 的请求（游戏 WS）透传 upgrade。
    # 写死 Connection "" 会盖掉 location 里的设置，握手到不了后端。
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header Connection $connection_upgrade;
    proxy_connect_timeout 5s;
    proxy_read_timeout 60s;
    add_header Strict-Transport-Security "max-age=31536000" always;

    # certbot webroot 校验
    location ^~ /.well-known/acme-challenge/ {
        root /var/www/letsencrypt;
    }

    if ($is_go_client) {
        return 301 https://www.google.com;
    }

    # companion-agent（陪伴 AI）：/v1/ 路由到 agent 机 104.160.191.87:8081
    # SSE 长连接必须关缓冲，否则回复等整段才到 App
    location ^~ /v1/ {
        proxy_pass http://ca_api;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_buffering off;
        proxy_cache off;
        proxy_read_timeout 3600s;
        client_max_body_size 32m;
    }
    location = /companion-health {
        proxy_pass http://ca_api/health;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
    }

    # Prometheus 抓取点。指标里有各模型的调用量、token 数和各会话的延迟分布，
    # 能反推出业务体量，所以只对本机与内网放开，不对公网。
    # ^~ 前缀匹配：/metrics 与 /metrics/snapshot 都要代理（面板读 JSON，Prometheus 读文本）。
    # 用精确匹配 = 会让 /metrics/snapshot 掉到默认 location 返回 404。
    location ^~ /metrics {
        allow 127.0.0.1;
        allow 10.0.0.0/8;
        allow 172.16.0.0/12;
        allow 192.168.0.0/16;
        deny all;
        proxy_pass http://ca_api/metrics;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        access_log off;
    }

    # 游戏模块 WebSocket。两个坑（都踩过，别改回去）：
    # 1. rewrite ... break 写在 proxy_pass 前面会旁路本 location 的 proxy_set_header，
    #    后端收到 Host: <upstream 名> + Connection: close，握手 400。路径改写用带 URI
    #    的 proxy_pass 完成。
    # 2. Host 写死 127.0.0.1:8888：后端按 Host 路由，$host/$proxy_host 都会解析成
    #    upstream 名，握手被拒。
    # 上游用 vpn_game（固定本机 8888）：远端 104.160.191.19 的 jar 没有 game 模块。
    location ^~ /vvv/api/game/ws {
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection $connection_upgrade;
        proxy_set_header Host 127.0.0.1:8888;
        proxy_read_timeout 300s;
        proxy_send_timeout 300s;
        proxy_pass http://vpn_game/api/game/ws;
    }
    # 游戏的普通接口：显式声明 JSON，同样优先于通用 /vvv/ 块。
    location ^~ /vvv/api/game/v1/ {
        default_type application/json;
        expires -1;
        rewrite ^/vvv(/.*)$ $1 break;
        proxy_pass http://vpn_game;
    }

    # 通用 API：/vvv 下的接口返回 JSON（VPN 主业务走 vpn_server 多机池）
    location /vvv/ {
        default_type application/json;
        expires -1;
        rewrite ^/vvv(/.*)$ $1 break;
        proxy_pass http://vpn_server;
    }

    # 视频条目
    location = /vvv/api/video/item {
        default_type application/json;
        expires -1;
        rewrite ^/vvv(/.*)$ $1 break;
        proxy_pass http://fetchurl_server;
    }

    # AI 文件 / OCR / 本地模型：精确或前缀匹配，优先于 /vvv/api/chat
    location = /vvv/api/chat/ai/file.json {
        default_type application/json;
        rewrite ^/vvv(/.*)$ $1 break;
        proxy_pass http://chat_server1;
    }
    location = /vvv/api/chat/ai/ocr.json {
        default_type application/json;
        rewrite ^/vvv(/.*)$ $1 break;
        proxy_pass http://chat_server1;
    }
    location ^~ /vvv/api/chat/ai/local {
        default_type application/json;
        rewrite ^/vvv(/.*)$ $1 break;
        proxy_pass http://chat_server1;
    }

    # 聊天接口：可能是流式输出，关闭缓冲，逐字返回
    location ^~ /vvv/api/chat {
        default_type application/json;
        proxy_buffering off;
        proxy_cache off;
        proxy_read_timeout 300s;
        rewrite ^/vvv(/.*)$ $1 break;
        proxy_pass http://chat_server;
    }

    location ^~ /vvv/api/test {
        default_type application/json;
        rewrite ^/vvv(/.*)$ $1 break;
        proxy_pass http://chat_server;
    }

    location ^~ /BookManager {
        proxy_pass http://book_server;
    }

    # 静态文件
    location ^~ /file/ {
        alias /home/file/html/;
    }
    location ^~ /image/ {
        alias /home/web/webroot/files/;
    }
    location ^~ /soft {
        alias /home/file/soft;
    }
    location = /favicon.ico {
        return 404;
    }

    # 站点首页
    location / {
        alias /home/file/html/;
        try_files $uri $uri/ =404;
    }
