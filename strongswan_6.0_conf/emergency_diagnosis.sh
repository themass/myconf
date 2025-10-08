#!/bin/bash

echo "=== strongSwan 6.0.2 紧急诊断 ==="

# 1. 检查 charon 可执行文件
echo "1. 检查 charon 可执行文件位置："
echo "查找 /usr/sbin/charon:"
ls -la /usr/sbin/charon 2>/dev/null || echo "❌ /usr/sbin/charon 不存在"

echo "查找 /usr/lib/ipsec/charon:"
ls -la /usr/lib/ipsec/charon 2>/dev/null || echo "❌ /usr/lib/ipsec/charon 不存在"

echo "查找 /usr/libexec/ipsec/charon:"
ls -la /usr/libexec/ipsec/charon 2>/dev/null || echo "❌ /usr/libexec/ipsec/charon 不存在"

echo "查找所有 charon 文件："
find /usr -name "charon" -type f 2>/dev/null || echo "❌ 未找到 charon 可执行文件"

# 2. 检查 strongSwan 安装状态
echo ""
echo "2. 检查 strongSwan 安装状态："
dpkg -l | grep strongswan

# 3. 检查 systemd 服务文件
echo ""
echo "3. 检查 systemd 服务文件："
cat /etc/systemd/system/strongswan.service

# 4. 检查可执行文件权限
echo ""
echo "4. 检查相关可执行文件："
ls -la /usr/sbin/ipsec* 2>/dev/null || echo "❌ /usr/sbin/ipsec* 不存在"
ls -la /usr/lib/ipsec/ 2>/dev/null || echo "❌ /usr/lib/ipsec/ 不存在"

# 5. 检查配置文件
echo ""
echo "5. 检查配置文件："
ls -la /etc/strongswan.conf 2>/dev/null || echo "❌ /etc/strongswan.conf 不存在"
ls -la /etc/swanctl/ 2>/dev/null || echo "❌ /etc/swanctl/ 不存在"

echo ""
echo "=== 诊断完成 ==="
