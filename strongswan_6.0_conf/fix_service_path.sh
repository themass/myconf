#!/bin/bash

echo "=== 修复 systemd 服务文件路径 ==="

# 1. 停止服务
echo "1. 停止服务..."
sudo systemctl stop strongswan 2>/dev/null || true

# 2. 检查 charon 实际位置
echo "2. 检查 charon 实际位置..."
find /usr -name "charon" -type f 2>/dev/null

# 3. 修复服务文件路径
echo "3. 修复服务文件路径..."
sudo sed -i 's|ExecStart=/usr/sbin/charon|ExecStart=/usr/lib/ipsec/charon|g' /etc/systemd/system/strongswan.service

# 4. 显示修复后的服务文件
echo "4. 修复后的服务文件："
cat /etc/systemd/system/strongswan.service

# 5. 重新加载 systemd
echo "5. 重新加载 systemd..."
sudo systemctl daemon-reload

# 6. 尝试启动服务
echo "6. 尝试启动服务..."
sudo systemctl start strongswan
sleep 3

# 7. 检查服务状态
echo "7. 检查服务状态..."
sudo systemctl status strongswan --no-pager

echo ""
echo "=== 修复完成 ==="
