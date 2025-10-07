#!/bin/bash

echo "=== 修复 strongSwan 6.0.2 配置问题 ==="

# 停止所有 strongSwan 服务
echo "停止所有 strongSwan 服务..."
sudo systemctl stop strongswan 2>/dev/null || true
sudo systemctl stop strongswan-swanctl 2>/dev/null || true
sudo systemctl stop ipsec 2>/dev/null || true

# 清理旧的配置文件
echo "清理旧的配置文件..."
sudo rm -f /etc/strongswan.conf
sudo rm -f /etc/swanctl.conf
sudo rm -rf /etc/swanctl/x509/*
sudo rm -rf /etc/swanctl/private/*

# 重新生成证书
echo "重新生成证书..."
cd /tmp
rm -rf ca6
mkdir -p ca6
cd ca6

# 获取服务器IP
SERVER_IP=$(ip route get 1 | awk '{print $7; exit}')
echo "服务器IP: $SERVER_IP"

# 生成 CA 证书
echo "生成 CA 证书..."
ipsec pki --gen --outform pem > caKey.pem
ipsec pki --self --in caKey.pem --dn "C=CN, O=timeline, CN=$SERVER_IP" --ca --outform pem > caCert.pem

# 生成服务器证书
echo "生成服务器证书..."
ipsec pki --gen --outform pem > serverKey.pem
ipsec pki --pub --in serverKey.pem | ipsec pki --issue --cacert caCert.pem --cakey caKey.pem --dn "C=CN, O=timeline, CN=$SERVER_IP" --san="$SERVER_IP" --flag serverAuth --flag ikeIntermediate --outform pem > serverCert.pem

# 生成客户端证书
echo "生成客户端证书..."
ipsec pki --gen --outform pem > clientKey.pem
ipsec pki --pub --in clientKey.pem | ipsec pki --issue --cacert caCert.pem --cakey caKey.pem --dn "C=CN, O=timeline, CN=client" --outform pem > clientCert.pem

# 生成 PKCS12 格式客户端证书
echo "生成 PKCS12 客户端证书..."
openssl pkcs12 -export -inkey clientKey.pem -in clientCert.pem -name "client" -certfile caCert.pem -caname "$SERVER_IP" -out clientCert.p12 -passout pass:

# 注意：证书和端口无关，只需要一套证书即可

# 复制到 strongSwan 6.0.2 目录
echo "复制证书到 strongSwan 6.0.2 目录..."
sudo mkdir -p /etc/swanctl/{x509,private}

# 复制基础证书
sudo cp caCert.pem /etc/swanctl/x509/
sudo cp serverCert.pem /etc/swanctl/x509/
sudo cp serverKey.pem /etc/swanctl/private/
sudo cp clientCert.pem /etc/swanctl/x509/
sudo cp clientKey.pem /etc/swanctl/private/

# 注意：端口配置不需要额外的证书，使用同一套证书即可

# 设置权限
echo "设置证书权限..."
sudo chown -R strongswan:strongswan /etc/swanctl
sudo chmod 644 /etc/swanctl/x509/*.pem
sudo chmod 600 /etc/swanctl/private/*.pem

# 复制配置文件
echo "复制配置文件..."
cd /Users/liguoqing/work/myconf/shell
sudo cp ../strongswan_6.0_conf/strongswan.conf /etc/strongswan.conf

# 复制 swanctl.conf 并替换 IP (包含端口配置)
sudo sed "s/{{SERVER_IP}}/$SERVER_IP/g" ../strongswan_6.0_conf/swanctl.conf.template > /tmp/swanctl.conf
sudo cp /tmp/swanctl.conf /etc/swanctl.conf
sudo rm /tmp/swanctl.conf

# 复制 updown 脚本
sudo mkdir -p /etc/swanctl/scripts
sudo cp ../strongswan_6.0_conf/updown.sh /etc/swanctl/scripts/
sudo chmod +x /etc/swanctl/scripts/updown.sh

# 重新加载 systemd 配置
echo "重新加载 systemd 配置..."
sudo systemctl daemon-reload

# 启动服务
echo "启动服务..."
sudo systemctl start strongswan

# 等待服务启动
sleep 3

# 检查服务状态
echo "检查服务状态..."
if sudo systemctl is-active --quiet strongswan; then
    echo "✅ strongSwan 6.0.2 修复成功！"
    echo "服务状态："
    sudo systemctl status strongswan --no-pager -l
    echo ""
    echo "端口监听情况："
    sudo netstat -tulpn | grep -E "(500|4500|8080|8081)"
    echo ""
    echo "连接配置："
    sudo swanctl --list-conns
else
    echo "❌ 服务启动失败，请检查日志："
    sudo journalctl -u strongswan --no-pager -n 20
fi

echo "=== 修复完成 ==="
