#!/bin/bash

echo "=== 检查 strongSwan 6.0.2 问题 ==="

# 1. 检查配置文件语法
echo "1. 检查配置文件语法..."
if command -v strongswan >/dev/null 2>&1; then
    strongswan --check-config /etc/strongswan.conf
    echo "配置文件语法检查完成"
else
    echo "strongswan 命令不可用，跳过语法检查"
fi

# 2. 检查服务状态
echo ""
echo "2. 检查服务状态..."
systemctl status strongswan --no-pager -l

# 3. 检查日志
echo ""
echo "3. 检查最近日志..."
journalctl -u strongswan -n 20 --no-pager

# 4. 检查目录权限
echo ""
echo "4. 检查目录权限..."
ls -la /var/run/charon/ 2>/dev/null || echo "/var/run/charon/ 不存在"
ls -la /var/log/strongswan/ 2>/dev/null || echo "/var/log/strongswan/ 不存在"
ls -la /etc/swanctl/ 2>/dev/null || echo "/etc/swanctl/ 不存在"

# 5. 检查进程
echo ""
echo "5. 检查进程..."
ps aux | grep charon | grep -v grep || echo "没有 charon 进程运行"

# 6. 检查 socket 文件
echo ""
echo "6. 检查 socket 文件..."
ls -la /var/run/charon.vici 2>/dev/null || echo "/var/run/charon.vici 不存在"

echo ""
echo "=== 检查完成 ==="
