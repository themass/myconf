#!/bin/bash

# strongSwan 6.0.2 重启问题修复脚本
# 解决 systemctl restart strongswan 卡死的问题

echo "=== 修复 strongSwan 重启卡死问题 ==="

# 1. 强制停止所有 strongSwan 相关进程
echo "1. 强制停止所有 strongSwan 相关进程..."
sudo pkill -f charon
sudo pkill -f strongswan
sleep 2

# 2. 清理 VICI socket 文件
echo "2. 清理 VICI socket 文件..."
sudo rm -f /var/run/charon.vici
sudo rm -f /var/run/charon/*

# 3. 清理可能的锁文件
echo "3. 清理锁文件..."
sudo rm -f /var/lock/charon.lock
sudo rm -f /var/run/charon.pid

# 4. 重置 systemd 服务状态
echo "4. 重置 systemd 服务状态..."
sudo systemctl reset-failed strongswan

# 5. 重新加载 systemd 配置
echo "5. 重新加载 systemd 配置..."
sudo systemctl daemon-reload

# 6. 启动服务
echo "6. 启动 strongSwan 服务..."
sudo systemctl start strongswan

# 7. 检查服务状态
echo "7. 检查服务状态..."
sleep 3
if sudo systemctl is-active --quiet strongswan; then
    echo "✅ strongSwan 服务启动成功！"
    echo "服务状态："
    sudo systemctl status strongswan --no-pager -l
else
    echo "❌ strongSwan 服务启动失败"
    echo "错误日志："
    sudo journalctl -u strongswan --no-pager -n 20
fi

echo "=== 修复完成 ==="
