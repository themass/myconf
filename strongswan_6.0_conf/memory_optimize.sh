#!/bin/bash

echo "=== 512M内存系统优化脚本 ==="

# 1. 清理系统缓存
echo "1. 清理系统缓存..."
sudo sync
echo 3 | sudo tee /proc/sys/vm/drop_caches > /dev/null

# 2. 检查内存使用
echo "2. 当前内存使用："
free -h

# 3. 停止不必要的服务
echo "3. 停止不必要的服务..."
sudo systemctl stop apache2 2>/dev/null || true
sudo systemctl stop nginx 2>/dev/null || true
sudo systemctl stop mysql 2>/dev/null || true
sudo systemctl stop postgresql 2>/dev/null || true

# 4. 设置内存限制
echo "4. 设置内存限制..."
echo "vm.swappiness=10" | sudo tee -a /etc/sysctl.conf
echo "vm.vfs_cache_pressure=50" | sudo tee -a /etc/sysctl.conf
sudo sysctl -p

# 5. 使用低内存配置
echo "5. 使用低内存配置..."
sudo cp /root/work/myconf/strongswan_6.0_conf/strongswan.conf.lowmem /etc/strongswan.conf

# 6. 检查内存使用
echo "6. 优化后内存使用："
free -h

echo "=== 内存优化完成 ==="
echo "现在可以尝试启动 strongSwan："
echo "sudo systemctl start strongswan"
