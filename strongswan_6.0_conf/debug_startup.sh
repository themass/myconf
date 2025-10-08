#!/bin/bash

echo "=== strongSwan 启动调试脚本 ==="

# 1. 检查服务状态
echo "1. 检查服务状态..."
sudo systemctl status strongswan --no-pager -l

# 2. 检查进程
echo "2. 检查进程..."
ps aux | grep -E "(charon|strongswan)" | grep -v grep

# 3. 检查日志
echo "3. 检查最新日志..."
sudo journalctl -u strongswan --no-pager -n 20

# 4. 检查配置文件
echo "4. 检查配置文件..."
echo "strongswan.conf 前10行："
head -10 /etc/strongswan.conf
echo ""
echo "swanctl.conf 前10行："
head -10 /etc/swanctl/swanctl.conf

# 5. 检查端口占用
echo "5. 检查端口占用..."
sudo netstat -tulpn | grep -E "(8080|8081|500|4500)"

# 6. 检查证书文件
echo "6. 检查证书文件..."
ls -la /etc/swanctl/x509/ 2>/dev/null || echo "证书目录不存在"
ls -la /etc/swanctl/private/ 2>/dev/null || echo "私钥目录不存在"

# 7. 手动测试配置加载
echo "7. 手动测试配置加载..."
sudo swanctl --load-all 2>&1 | head -10

echo "=== 调试完成 ==="
