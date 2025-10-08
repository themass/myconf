#!/bin/bash

echo "=== 强制清理 strongSwan 进程和资源 ==="

# 1. 强制停止所有相关服务
echo "强制停止所有 strongSwan 相关服务..."
sudo systemctl stop strongswan 2>/dev/null || true
sudo systemctl stop strongswan-swanctl 2>/dev/null || true
sudo systemctl stop ipsec 2>/dev/null || true

# 2. 强制杀死所有 charon 进程
echo "强制杀死所有 charon 进程..."
sudo pkill -9 -f charon 2>/dev/null || true
sudo pkill -9 -f strongswan 2>/dev/null || true
sudo pkill -9 -f ipsec 2>/dev/null || true

# 3. 等待进程完全退出
echo "等待进程完全退出..."
sleep 5

# 4. 检查是否还有进程在运行
echo "检查残留进程..."
if pgrep -f charon > /dev/null; then
    echo "发现残留的 charon 进程，强制杀死..."
    sudo pkill -9 -f charon
    sleep 2
fi

# 5. 清理所有 socket 文件和锁文件
echo "清理 socket 文件和锁文件..."
sudo rm -f /var/run/charon.vici
sudo rm -f /var/run/charon/*
sudo rm -f /var/run/strongswan*
sudo rm -f /var/lock/strongswan*
sudo rm -f /tmp/strongswan*

# 6. 清理网络接口
echo "清理网络接口..."
sudo ip xfrm state flush 2>/dev/null || true
sudo ip xfrm policy flush 2>/dev/null || true

# 7. 重新创建目录和文件
echo "重新创建目录和文件..."
sudo mkdir -p /var/log/strongswan
sudo mkdir -p /etc/swanctl/{private,x509,scripts}
sudo mkdir -p /var/run/charon

# 8. 设置正确的权限
echo "设置正确的权限..."
sudo chown -R strongswan:strongswan /var/log/strongswan /etc/swanctl /var/run/charon
sudo chmod 755 /var/log/strongswan /etc/swanctl /var/run/charon
sudo chmod 700 /etc/swanctl/private

# 9. 重新加载 systemd
echo "重新加载 systemd..."
sudo systemctl daemon-reload

# 10. 检查清理结果
echo "检查清理结果..."
echo "残留进程："
pgrep -f charon || echo "没有残留的 charon 进程"
echo "Socket 文件："
ls -la /var/run/charon* 2>/dev/null || echo "没有 socket 文件"

echo "=== 强制清理完成 ==="
echo "现在可以尝试启动 strongSwan 服务"
