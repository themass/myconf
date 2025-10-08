#!/bin/bash

echo "=== 修复 charon 可执行文件丢失问题 ==="

# 1. 检查当前安装状态
echo "1. 检查 strongSwan 安装状态："
dpkg -l | grep strongswan

# 2. 查找 charon 文件
echo ""
echo "2. 查找 charon 可执行文件："
find /usr -name "charon" -type f 2>/dev/null

# 3. 重新安装 strongSwan 6.0.2
echo ""
echo "3. 重新安装 strongSwan 6.0.2..."
sudo apt-get update
sudo apt-get install -y --reinstall strongswan strongswan-swanctl strongswan-charon

# 4. 再次查找 charon
echo ""
echo "4. 重新安装后查找 charon："
find /usr -name "charon" -type f 2>/dev/null

# 5. 检查 systemd 服务文件
echo ""
echo "5. 检查 systemd 服务文件："
if [ -f /etc/systemd/system/strongswan.service ]; then
    echo "当前服务文件："
    cat /etc/systemd/system/strongswan.service
else
    echo "❌ 服务文件不存在，创建默认服务文件..."
    sudo tee /etc/systemd/system/strongswan.service > /dev/null << 'EOF'
[Unit]
Description=strongSwan IPsec daemon
After=network.target

[Service]
Type=notify
ExecStart=/usr/lib/ipsec/charon --use-syslog
ExecReload=/bin/kill -HUP $MAINPID
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF
fi

# 6. 重新加载 systemd
echo ""
echo "6. 重新加载 systemd..."
sudo systemctl daemon-reload

# 7. 尝试启动
echo ""
echo "7. 尝试启动服务..."
sudo systemctl start strongswan
sudo systemctl status strongswan --no-pager

echo ""
echo "=== 修复完成 ==="
