#!/bin/bash

echo "=== 修复 strongSwan 6.0.2 权限问题 ==="

# 停止服务
echo "停止 strongSwan 服务..."
sudo systemctl stop strongswan 2>/dev/null || true
sudo systemctl stop strongswan-swanctl 2>/dev/null || true
sudo pkill -f charon 2>/dev/null || true

# 清理旧的 socket 文件
echo "清理旧的 socket 文件..."
sudo rm -f /var/run/charon.vici
sudo rm -f /var/run/charon/*

# 创建必要的目录
echo "创建必要的目录..."
sudo mkdir -p /var/log/strongswan
sudo mkdir -p /etc/swanctl/{private,x509,scripts}
sudo mkdir -p /var/run/charon

# 设置目录权限
echo "设置目录权限..."
sudo chown -R strongswan:strongswan /var/log/strongswan /etc/swanctl /var/run/charon
sudo chmod 755 /var/log/strongswan /etc/swanctl /var/run/charon
sudo chmod 700 /etc/swanctl/private

# 创建 VICI socket 文件并设置权限
echo "创建 VICI socket 文件..."
sudo touch /var/run/charon.vici
sudo chown strongswan:strongswan /var/run/charon.vici
sudo chmod 660 /var/run/charon.vici

# 重新加载 systemd
echo "重新加载 systemd..."
sudo systemctl daemon-reload

# 启动服务
echo "启动 strongSwan 服务..."
sudo systemctl start strongswan

# 检查状态
echo "检查服务状态..."
sleep 3
if sudo systemctl is-active --quiet strongswan; then
    echo "✅ strongSwan 服务启动成功！"
    sudo systemctl status strongswan --no-pager -l
else
    echo "❌ strongSwan 服务启动失败"
    echo "服务日志："
    sudo systemctl status strongswan --no-pager -l
    echo "详细日志："
    sudo journalctl -u strongswan --no-pager -n 20
fi

echo "=== 权限修复完成 ==="
