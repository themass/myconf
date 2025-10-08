#!/bin/bash

echo "=== 紧急安装 strongSwan 6.0.2 ==="

# 1. 检查系统
echo "1. 检查系统信息："
uname -a
cat /etc/os-release

# 2. 停止所有相关服务
echo "2. 停止所有相关服务..."
sudo systemctl stop strongswan 2>/dev/null || true
sudo pkill -f charon 2>/dev/null || true
sudo pkill -f strongswan 2>/dev/null || true

# 3. 安装基础依赖
echo "3. 安装基础依赖..."
sudo apt-get update
sudo apt-get install -y \
    build-essential \
    libssl-dev \
    libgmp-dev \
    libcurl4-openssl-dev \
    pkg-config \
    autotools-dev \
    libtool \
    autoconf \
    automake \
    libsystemd-dev \
    libiptc-dev \
    libip4tc-dev \
    libip6tc-dev \
    libpam0g-dev \
    libmysqlclient-dev \
    libsqlite3-dev \
    libldap2-dev \
    libsoup2.4-dev \
    libunbound-dev

# 4. 下载 strongSwan 6.0.2 源码
echo "4. 下载 strongSwan 6.0.2 源码..."
cd /tmp
if [ ! -f "strongswan-6.0.2.tar.bz2" ]; then
    wget https://download.strongswan.org/strongswan-6.0.2.tar.bz2 --no-check-certificate
    if [ $? -ne 0 ]; then
        echo "官方源下载失败，尝试备用源..."
        wget https://github.com/strongswan/strongswan/archive/refs/tags/6.0.2.tar.gz --no-check-certificate
        if [ $? -eq 0 ]; then
            tar -xzf 6.0.2.tar.gz
            mv strongswan-6.0.2 strongswan-6.0.2
        else
            echo "❌ 下载失败，请检查网络连接"
            exit 1
        fi
    else
        tar -jxvf strongswan-6.0.2.tar.bz2
    fi
fi

cd strongswan-6.0.2

# 5. 配置编译选项
echo "5. 配置编译选项..."
./configure \
    --prefix=/usr \
    --sysconfdir=/etc \
    --enable-openssl \
    --enable-nat-transport \
    --enable-eap-radius \
    --enable-eap-identity \
    --enable-eap-md5 \
    --enable-eap-mschapv2 \
    --enable-eap-tls \
    --enable-eap-ttls \
    --enable-eap-peap \
    --enable-eap-aka \
    --enable-eap-aka-3gpp2 \
    --enable-eap-gtc \
    --enable-eap-sim \
    --enable-eap-simaka-pseudonym \
    --enable-eap-simaka-reauth \
    --enable-eap-tnc \
    --enable-vici \
    --enable-swanctl \
    --enable-systemd \
    --enable-kernel-netlink \
    --enable-kernel-libipsec \
    --enable-forecast \
    --enable-fips-prf \
    --enable-gmp \
    --enable-md4 \
    --enable-md5 \
    --enable-mgf1 \
    --enable-pkcs12 \
    --enable-random \
    --enable-rc2 \
    --enable-sha1 \
    --enable-sha2 \
    --enable-tnc-tnccs \
    --enable-nonce \
    --enable-x509 \
    --enable-revocation \
    --enable-constraints \
    --enable-pubkey \
    --enable-pkcs1 \
    --enable-pkcs7 \
    --enable-pgp \
    --enable-dnskey \
    --enable-sshkey \
    --enable-pem \
    --enable-pkcs8 \
    --enable-xcbc \
    --enable-cmac \
    --enable-kdf \
    --enable-drbg \
    --enable-attr \
    --enable-resolve \
    --enable-socket-default \
    --enable-updown \
    --enable-xauth-generic \
    --enable-counters

if [ $? -ne 0 ]; then
    echo "❌ 配置失败，请检查依赖是否完整安装"
    exit 1
fi

# 6. 编译和安装
echo "6. 编译和安装..."
make -j$(nproc) && sudo make install
if [ $? -ne 0 ]; then
    echo "❌ 编译或安装失败"
    exit 1
fi

# 7. 创建 strongswan 用户和组
echo "7. 创建 strongswan 用户和组..."
if ! id "strongswan" &>/dev/null; then
    sudo groupadd -r strongswan 2>/dev/null || true
    sudo useradd -r -g strongswan -s /bin/false -d /var/lib/strongswan strongswan 2>/dev/null || true
    echo "✅ strongswan 用户创建完成"
else
    echo "✅ strongswan 用户已存在"
fi

# 8. 创建必要目录
echo "8. 创建必要目录..."
sudo mkdir -p /etc/swanctl/{private,x509,scripts}
sudo mkdir -p /var/log/strongswan
sudo mkdir -p /var/lib/strongswan
sudo mkdir -p /var/run/charon

# 9. 设置权限
echo "9. 设置权限..."
sudo chown -R strongswan:strongswan /etc/swanctl /var/log/strongswan /var/lib/strongswan /var/run/charon 2>/dev/null || true
sudo chmod 700 /etc/swanctl/private 2>/dev/null || true
sudo chmod 755 /var/lib/strongswan 2>/dev/null || true

# 10. 创建 systemd 服务文件
echo "10. 创建 systemd 服务文件..."
sudo tee /etc/systemd/system/strongswan.service > /dev/null << 'EOF'
[Unit]
Description=strongSwan IPsec daemon
After=network.target

[Service]
Type=notify
User=strongswan
Group=strongswan
ExecStart=/usr/lib/ipsec/charon --use-syslog
ExecReload=/bin/kill -HUP $MAINPID
Restart=on-failure
RestartSec=5s
RuntimeDirectory=charon
RuntimeDirectoryMode=0755
PrivateTmp=true
NoNewPrivileges=true

[Install]
WantedBy=multi-user.target
EOF

# 11. 重新加载 systemd
echo "11. 重新加载 systemd..."
sudo systemctl daemon-reload
sudo systemctl enable strongswan

# 12. 验证安装
echo "12. 验证安装..."
echo "charon 位置："
ls -la /usr/lib/ipsec/charon 2>/dev/null || echo "❌ /usr/lib/ipsec/charon 不存在"
ls -la /usr/sbin/charon 2>/dev/null || echo "❌ /usr/sbin/charon 不存在"

echo "swanctl 位置："
which swanctl 2>/dev/null || echo "❌ swanctl 不存在"

# 13. 启动服务
echo "13. 启动服务..."
sudo systemctl start strongswan
sleep 3

# 14. 检查服务状态
echo "14. 检查服务状态..."
if sudo systemctl is-active --quiet strongswan; then
    echo "✅ strongSwan 6.0.2 安装成功！"
    echo "服务状态："
    sudo systemctl status strongswan --no-pager -l
    echo ""
    echo "验证安装："
    echo "swanctl 版本：$(swanctl --version 2>/dev/null | head -1 || echo 'unknown')"
    echo "charon 位置：$(which charon 2>/dev/null || echo '/usr/lib/ipsec/charon')"
else
    echo "❌ 服务启动失败，请检查日志："
    sudo journalctl -u strongswan --no-pager -n 20
    echo ""
    echo "检查 charon 可执行文件："
    ls -la /usr/lib/ipsec/charon 2>/dev/null || echo "❌ /usr/lib/ipsec/charon 不存在"
    ls -la /usr/sbin/charon 2>/dev/null || echo "❌ /usr/sbin/charon 不存在"
    exit 1
fi

echo ""
echo "=== 紧急安装完成 ==="
echo "下一步："
echo "1. 运行配置：bash vpn_setup.sh strongswanconf6"
echo "2. 生成证书：bash vpn_setup.sh caip6"
