#!/bin/bash

echo "=== 强制清理 strongSwan 进程 ==="

# 1. 强制停止所有相关进程
echo "1. 强制停止所有相关进程..."
sudo pkill -9 -f charon 2>/dev/null || true
sudo pkill -9 -f strongswan 2>/dev/null || true
sudo pkill -9 -f ipsec 2>/dev/null || true

# 2. 停止 systemd 服务
echo "2. 停止 systemd 服务..."
sudo systemctl stop strongswan 2>/dev/null || true
sudo systemctl kill strongswan 2>/dev/null || true

# 3. 清理 socket 文件
echo "3. 清理 socket 文件..."
sudo rm -f /var/run/charon.vici
sudo rm -f /var/run/charon/*
sudo rm -f /var/lock/charon.lock
sudo rm -f /var/run/charon.pid

# 4. 重置 systemd 失败状态
echo "4. 重置 systemd 失败状态..."
sudo systemctl reset-failed strongswan 2>/dev/null || true

# 5. 检查进程
echo "5. 检查剩余进程..."
ps aux | grep -E "(charon|strongswan|ipsec)" | grep -v grep || echo "没有相关进程"

# 6. 检查端口占用
echo "6. 检查端口占用..."
netstat -tulpn | grep -E "(500|4500|8080|8081)" || echo "没有相关端口占用"

echo ""
echo "=== 清理完成 ==="
echo "现在可以重新运行配置："
echo "bash vpn_setup.sh strongswanconf6"
