#!/bin/bash
# 修复 strongSwan 用户和组问题的脚本

echo "=== 修复 strongSwan 用户和组问题 ==="

# 创建 strongswan 组（如果不存在）
if ! getent group strongswan >/dev/null 2>&1; then
    echo "创建 strongswan 组..."
    sudo groupadd -r strongswan
else
    echo "strongswan 组已存在"
fi

# 创建 strongswan 用户（如果不存在）
if ! id "strongswan" &>/dev/null; then
    echo "创建 strongswan 用户..."
    sudo useradd -r -s /bin/false -d /var/lib/strongswan -g strongswan strongswan
else
    echo "strongswan 用户已存在"
    # 确保用户属于正确的组
    sudo usermod -g strongswan strongswan 2>/dev/null || true
fi

# 创建必要的目录
echo "创建必要的目录..."
sudo mkdir -p /var/lib/strongswan
sudo mkdir -p /var/run/charon
sudo mkdir -p /var/log/strongswan

# 设置正确的权限
echo "设置权限..."
sudo chown -R strongswan:strongswan /var/lib/strongswan /var/run/charon /var/log/strongswan
sudo chown -R strongswan:strongswan /etc/swanctl 2>/dev/null || true

# 重新加载 systemd
echo "重新加载 systemd..."
sudo systemctl daemon-reload

# 停止并启动服务
echo "重启服务..."
sudo systemctl stop strongswan-swanctl 2>/dev/null || true
sudo systemctl start strongswan-swanctl

# 检查服务状态
echo "检查服务状态..."
if sudo systemctl is-active --quiet strongswan-swanctl; then
    echo "✅ strongSwan 服务启动成功！"
    sudo systemctl status strongswan-swanctl --no-pager -l
else
    echo "❌ 服务启动失败，查看日志："
    sudo journalctl -u strongswan-swanctl --no-pager -n 20
fi

echo "=== 修复完成 ==="
