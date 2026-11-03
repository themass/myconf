#!/usr/bin/env bash
# 自签名证书：仅用于测试 HTTPS 配置。
# 注意：Android 不信任自签名证书，AdMob 的服务端回调也会拒绝，正式环境请用 certbot.sh。
#
# 用法（root 执行）：
#   bash self-signed.sh
set -euo pipefail

DOMAINS=(api.ok123find.top file.ok123find.top)
SSL_DIR="${SSL_DIR:-/root/local/nginx/conf/ssl}"
NGINX_BIN="${NGINX_BIN:-/root/local/nginx/sbin/nginx}"
DAYS=365

if [[ $EUID -ne 0 ]]; then
    echo "请用 root 执行" >&2
    exit 1
fi

mkdir -p "$SSL_DIR"
cd "$SSL_DIR"

# 生成带 SAN 的配置，浏览器和 curl 才会接受
{
    echo "[req]"
    echo "distinguished_name = dn"
    echo "x509_extensions = v3"
    echo "prompt = no"
    echo "[dn]"
    echo "CN = ${DOMAINS[0]}"
    echo "[v3]"
    echo "subjectAltName = @alt"
    echo "basicConstraints = CA:FALSE"
    echo "keyUsage = digitalSignature, keyEncipherment"
    echo "extendedKeyUsage = serverAuth"
    echo "[alt]"
    i=1
    for d in "${DOMAINS[@]}"; do
        echo "DNS.$i = $d"
        i=$((i + 1))
    done
} > openssl-san.cnf

openssl req -x509 -nodes -newkey rsa:2048 -days "$DAYS" \
    -keyout privkey.pem -out fullchain.pem \
    -config openssl-san.cnf -extensions v3

chmod 600 privkey.pem
chmod 644 fullchain.pem
echo "已生成：$SSL_DIR/fullchain.pem 与 privkey.pem（有效期 ${DAYS} 天）"

"$NGINX_BIN" -t && "$NGINX_BIN" -s reload
echo "nginx 已重载。本地测试：curl -vk https://${DOMAINS[0]}/vvv/api/version.json"
