#!/bin/bash

echo "=== 简单清理 strongSwan ==="

# 1. 停止服务
echo "停止服务..."
sudo systemctl stop strongswan 2>/dev/null || true
sudo systemctl stop strongswan-swanctl 2>/dev/null || true

# 2. 杀死进程
echo "杀死进程..."
sudo pkill -f charon 2>/dev/null || true
sleep 2

# 3. 清理文件
echo "清理文件..."
sudo rm -f /var/run/charon.vici
sudo rm -f /var/run/charon/*

# 4. 创建目录
echo "创建目录..."
sudo mkdir -p /var/run/charon
sudo mkdir -p /var/log/strongswan
sudo mkdir -p /etc/swanctl/{private,x509,scripts}

# 5. 设置权限
echo "设置权限..."
sudo chown -R strongswan:strongswan /var/run/charon /var/log/strongswan /etc/swanctl
sudo chmod 755 /var/run/charon /var/log/strongswan /etc/swanctl
sudo chmod 700 /etc/swanctl/private

echo "=== 清理完成 ==="
