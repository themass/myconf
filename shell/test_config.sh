#!/bin/bash

# 测试 strongSwan 6.0.2 配置文件的语法和结构
# 不需要 sudo 权限，只验证配置文件

echo "=== 测试 strongSwan 6.0.2 配置文件 ==="

# 检查配置文件是否存在
echo "检查配置文件..."
if [ -f "../strongswan_6.0_conf/strongswan.conf" ]; then
    echo "✅ strongswan.conf 存在"
else
    echo "❌ strongswan.conf 不存在"
    exit 1
fi

if [ -f "../strongswan_6.0_conf/swanctl.conf.minimal" ]; then
    echo "✅ swanctl.conf.minimal 存在"
else
    echo "❌ swanctl.conf.minimal 不存在"
    exit 1
fi

# 检查配置文件语法
echo ""
echo "检查配置文件语法..."

# 检查 strongswan.conf 语法
echo "检查 strongswan.conf 语法..."
if command -v strongswan >/dev/null 2>&1; then
    strongswan --check-config ../strongswan_6.0_conf/strongswan.conf
    if [ $? -eq 0 ]; then
        echo "✅ strongswan.conf 语法正确"
    else
        echo "❌ strongswan.conf 语法错误"
    fi
else
    echo "⚠️  strongswan 命令不可用，跳过语法检查"
fi

# 检查 swanctl.conf 语法
echo "检查 swanctl.conf.minimal 语法..."
if command -v swanctl >/dev/null 2>&1; then
    swanctl --load-all --file ../strongswan_6.0_conf/swanctl.conf.minimal
    if [ $? -eq 0 ]; then
        echo "✅ swanctl.conf.minimal 语法正确"
    else
        echo "❌ swanctl.conf.minimal 语法错误"
    fi
else
    echo "⚠️  swanctl 命令不可用，跳过语法检查"
fi

# 显示配置文件内容
echo ""
echo "=== strongswan.conf 内容 ==="
cat ../strongswan_6.0_conf/strongswan.conf

echo ""
echo "=== swanctl.conf.minimal 内容 ==="
cat ../strongswan_6.0_conf/swanctl.conf.minimal

echo ""
echo "=== 测试完成 ==="
echo "如果配置文件语法正确，可以在服务器上运行："
echo "bash vpn_setup.sh strongswanconf_minimal"
