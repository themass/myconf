#!/usr/bin/env bash
# Let's Encrypt 正式证书（免费，Android 与 AdMob 都信任）。
#
# 前提：
#   1. 域名 api.ok123find.top、file.ok123find.top 的 A 记录指向本服务器；
#   2. 服务器 80 端口可以从公网访问（Let's Encrypt 通过它校验域名）。
#
# 用法（root 执行）：
#   bash certbot.sh 你的邮箱@example.com
set -euo pipefail

EMAIL="${1:?用法: $0 你的邮箱}"
DOMAINS=(api.ok123find.top file.ok123find.top)
WEBROOT=/var/www/letsencrypt
SSL_DIR="${SSL_DIR:-/root/local/nginx/conf/ssl}"
NGINX_BIN="${NGINX_BIN:-/root/local/nginx/sbin/nginx}"
LIVE_DIR="/etc/letsencrypt/live/${DOMAINS[0]}"

if [[ $EUID -ne 0 ]]; then
    echo "请用 root 执行" >&2
    exit 1
fi

# 安装 certbot（CentOS / Alibaba Cloud Linux 用 yum，Debian/Ubuntu 用 apt）
if ! command -v certbot >/dev/null 2>&1; then
    if command -v yum >/dev/null 2>&1; then
        yum install -y epel-release || true
        yum install -y certbot
    else
        apt-get update && apt-get install -y certbot
    fi
fi

mkdir -p "$WEBROOT" "$SSL_DIR"

# 申请证书（webroot 方式：不会中断 nginx）
ARGS=()
for d in "${DOMAINS[@]}"; do ARGS+=(-d "$d"); done
certbot certonly --webroot -w "$WEBROOT" "${ARGS[@]}" \
    -m "$EMAIL" --agree-tos --non-interactive

# 复制到 nginx 使用的固定路径
cp -L "$LIVE_DIR/fullchain.pem" "$SSL_DIR/fullchain.pem"
cp -L "$LIVE_DIR/privkey.pem" "$SSL_DIR/privkey.pem"
chmod 600 "$SSL_DIR/privkey.pem"

# 续期后自动复制并重载 nginx
HOOK_DIR=/etc/letsencrypt/renewal-hooks/deploy
mkdir -p "$HOOK_DIR"
cat > "$HOOK_DIR/nginx-reload.sh" <<HOOK
#!/usr/bin/env bash
cp -L "$LIVE_DIR/fullchain.pem" "$SSL_DIR/fullchain.pem"
cp -L "$LIVE_DIR/privkey.pem" "$SSL_DIR/privkey.pem"
$NGINX_BIN -s reload
HOOK
chmod +x "$HOOK_DIR/nginx-reload.sh"

"$NGINX_BIN" -t && "$NGINX_BIN" -s reload
echo "证书已就绪。测试续期：certbot renew --dry-run"
echo "验证：curl -I https://${DOMAINS[0]}/vvv/api/version.json"
