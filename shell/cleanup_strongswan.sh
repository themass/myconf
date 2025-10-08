#!/bin/bash

echo "=== 清理 strongSwan 6.0.2 残留文件 ==="

# 1. 停止所有相关服务
echo "1. 停止服务..."
systemctl stop strongswan 2>/dev/null || true
systemctl stop strongswan-swanctl 2>/dev/null || true

# 2. 杀死所有 charon 进程
echo "2. 清理进程..."
pkill -f charon 2>/dev/null || true
sleep 2

# 3. 清理 socket 文件
echo "3. 清理 socket 文件..."
rm -f /var/run/charon.vici 2>/dev/null || true
rm -f /var/run/charon/* 2>/dev/null || true

# 4. 清理 PID 文件
echo "4. 清理 PID 文件..."
rm -f /var/run/charon.pid 2>/dev/null || true

# 5. 重新创建目录
echo "5. 重新创建目录..."
mkdir -p /var/run/charon
mkdir -p /var/log/strongswan
mkdir -p /etc/swanctl/{private,x509,scripts}

# 6. 设置权限
echo "6. 设置权限..."
chown -R strongswan:strongswan /var/run/charon /var/log/strongswan /etc/swanctl 2>/dev/null || true
chmod 755 /var/run/charon /var/log/strongswan /etc/swanctl
chmod 700 /etc/swanctl/private 2>/dev/null || true

# 7. 重新加载 systemd
echo "7. 重新加载 systemd..."
systemctl daemon-reload

echo "=== 清理完成 ==="
echo "现在可以重新启动 strongSwan："
echo "systemctl start strongswan"
