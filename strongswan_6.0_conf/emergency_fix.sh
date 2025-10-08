#!/bin/bash

echo "=== strongSwan 紧急修复脚本 ==="

# 1. 强制终止所有相关进程
echo "1. 强制终止所有相关进程..."
sudo pkill -9 -f charon
sudo pkill -9 -f strongswan
sudo pkill -9 -f ipsec
sleep 2

# 2. 清理所有相关文件
echo "2. 清理所有相关文件..."
sudo rm -f /var/run/charon.vici
sudo rm -f /var/run/charon/*
sudo rm -f /var/lock/charon.lock
sudo rm -f /var/run/charon.pid
sudo rm -f /var/run/strongswan.pid
sudo rm -f /tmp/charon.*

# 3. 重置 systemd 服务
echo "3. 重置 systemd 服务..."
sudo systemctl reset-failed strongswan
sudo systemctl daemon-reload

# 4. 检查配置文件语法
echo "4. 检查配置文件语法..."
if [ -f /etc/strongswan.conf ]; then
    echo "检查 strongswan.conf..."
    sudo charon --test-config
fi

if [ -f /etc/swanctl/swanctl.conf ]; then
    echo "检查 swanctl.conf..."
    sudo swanctl --test-config
fi

# 5. 尝试手动启动 charon 进行调试
echo "5. 尝试手动启动 charon 进行调试..."
sudo charon --debug-1 --use-syslog &
CHARON_PID=$!
sleep 5
sudo kill $CHARON_PID 2>/dev/null

# 6. 检查系统资源
echo "6. 检查系统资源..."
echo "内存使用："
free -h
echo "磁盘空间："
df -h /
echo "进程数："
ps aux | wc -l

echo "=== 修复完成，请检查输出 ==="
