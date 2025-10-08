#!/bin/bash

echo "=== 立即修复 strongSwan 服务 ==="

# 1. 停止服务
echo "1. 停止服务..."
sudo systemctl stop strongswan 2>/dev/null || true
sudo pkill -f charon 2>/dev/null || true

# 2. 创建正确的 systemd 服务文件
echo "2. 创建 systemd 服务文件..."
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

# 3. 重新加载 systemd
echo "3. 重新加载 systemd..."
sudo systemctl daemon-reload

# 4. 检查 charon 文件
echo "4. 检查 charon 文件..."
ls -la /usr/lib/ipsec/charon

# 5. 尝试启动服务
echo "5. 尝试启动服务..."
sudo systemctl start strongswan
sleep 3

# 6. 检查服务状态
echo "6. 检查服务状态..."
sudo systemctl status strongswan --no-pager

echo ""
echo "=== 修复完成 ==="
