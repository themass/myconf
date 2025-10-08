#!/bin/bash

echo "=== 修复512M内存启动问题 ==="

# 1. 停止服务
echo "1. 停止服务..."
sudo systemctl stop strongswan
sudo pkill -9 -f charon

# 2. 清理内存
echo "2. 清理内存..."
sudo sync
echo 3 | sudo tee /proc/sys/vm/drop_caches > /dev/null

# 3. 检查内存
echo "3. 当前内存："
free -h

# 4. 使用超低内存配置
echo "4. 使用超低内存配置..."
sudo cp /root/work/myconf/strongswan_6.0_conf/strongswan.conf.ultra_lowmem /etc/strongswan.conf

# 5. 修改systemd超时时间
echo "5. 修改systemd超时时间..."
sudo mkdir -p /etc/systemd/system/strongswan.service.d
sudo tee /etc/systemd/system/strongswan.service.d/timeout.conf > /dev/null << EOF
[Service]
TimeoutStartSec=300
TimeoutStopSec=30
EOF

# 6. 重新加载systemd
echo "6. 重新加载systemd..."
sudo systemctl daemon-reload

# 7. 检查内存
echo "7. 优化后内存："
free -h

echo "=== 修复完成 ==="
echo "现在尝试启动："
echo "sudo systemctl start strongswan"
echo ""
echo "如果还是卡死，请运行："
echo "sudo charon --debug-dmn 2 --use-syslog"
