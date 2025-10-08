#!/bin/bash

echo "=== 测试 strongSwan 6.0.2 最简配置 ==="

# 1. 强制清理
echo "1. 强制清理..."
bash /root/work/myconf/shell/force_clean_strongswan.sh

# 2. 使用最简配置
echo "2. 使用最简配置..."
sudo cp /root/work/myconf/strongswan_6.0_conf/strongswan.conf.test /etc/strongswan.conf

# 3. 检查配置文件语法
echo "3. 检查配置文件语法..."
if command -v strongswan >/dev/null 2>&1; then
    sudo strongswan --check-config /etc/strongswan.conf
    if [ $? -eq 0 ]; then
        echo "✅ 配置文件语法正确"
    else
        echo "❌ 配置文件语法错误"
        exit 1
    fi
else
    echo "⚠️  strongswan 命令不可用，跳过语法检查"
fi

# 4. 启动服务
echo "4. 启动服务..."
sudo systemctl start strongswan

# 5. 等待服务启动
echo "5. 等待服务启动..."
sleep 5

# 6. 检查服务状态
echo "6. 检查服务状态..."
if sudo systemctl is-active --quiet strongswan; then
    echo "✅ strongSwan 服务启动成功！"
    echo "服务状态："
    sudo systemctl status strongswan --no-pager -l
    echo ""
    echo "进程信息："
    ps aux | grep charon | grep -v grep
    echo ""
    echo "Socket 文件："
    ls -la /var/run/charon* 2>/dev/null || echo "没有 socket 文件"
else
    echo "❌ strongSwan 服务启动失败"
    echo "服务日志："
    sudo systemctl status strongswan --no-pager -l
    echo "详细日志："
    sudo journalctl -u strongswan --no-pager -n 20
    exit 1
fi

echo "=== 最简配置测试完成 ==="
