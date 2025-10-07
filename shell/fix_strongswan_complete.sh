#!/bin/bash
# 完整修复 strongSwan 6.0 部署问题的脚本

echo "=== 完整修复 strongSwan 6.0 部署问题 ==="

# 检查 charon 二进制文件
echo "1. 检查 charon 二进制文件..."
if [ -f "/usr/sbin/charon" ]; then
    echo "✅ charon 二进制文件存在: /usr/sbin/charon"
    ls -la /usr/sbin/charon
else
    echo "❌ charon 二进制文件不存在，检查其他位置..."
    find /usr -name "charon" -type f 2>/dev/null
    if [ $? -eq 0 ]; then
        CHARON_PATH=$(find /usr -name "charon" -type f 2>/dev/null | head -1)
        echo "找到 charon: $CHARON_PATH"
        # 创建符号链接
        sudo ln -sf "$CHARON_PATH" /usr/sbin/charon
        echo "创建符号链接: /usr/sbin/charon -> $CHARON_PATH"
    else
        echo "❌ 未找到 charon 二进制文件，请重新编译安装"
        exit 1
    fi
fi

# 检查 swanctl 二进制文件
echo "2. 检查 swanctl 二进制文件..."
if [ -f "/usr/sbin/swanctl" ]; then
    echo "✅ swanctl 二进制文件存在: /usr/sbin/swanctl"
    ls -la /usr/sbin/swanctl
else
    echo "❌ swanctl 二进制文件不存在，检查其他位置..."
    find /usr -name "swanctl" -type f 2>/dev/null
    if [ $? -eq 0 ]; then
        SWANCTL_PATH=$(find /usr -name "swanctl" -type f 2>/dev/null | head -1)
        echo "找到 swanctl: $SWANCTL_PATH"
        # 创建符号链接
        sudo ln -sf "$SWANCTL_PATH" /usr/sbin/swanctl
        echo "创建符号链接: /usr/sbin/swanctl -> $SWANCTL_PATH"
    else
        echo "❌ 未找到 swanctl 二进制文件，请重新编译安装"
        exit 1
    fi
fi

# 创建 strongswan 组
echo "3. 创建 strongswan 组..."
if ! getent group strongswan >/dev/null 2>&1; then
    sudo groupadd -r strongswan
    echo "✅ 创建了 strongswan 组"
else
    echo "✅ strongswan 组已存在"
fi

# 创建 strongswan 用户
echo "4. 创建 strongswan 用户..."
if ! id "strongswan" &>/dev/null; then
    sudo useradd -r -s /bin/false -d /var/lib/strongswan -g strongswan strongswan
    echo "✅ 创建了 strongswan 用户"
else
    echo "✅ strongswan 用户已存在"
    # 确保用户属于正确的组
    sudo usermod -g strongswan strongswan 2>/dev/null || true
fi

# 创建必要的目录
echo "5. 创建必要的目录..."
sudo mkdir -p /var/lib/strongswan
sudo mkdir -p /var/run/charon
sudo mkdir -p /var/log/strongswan
sudo mkdir -p /etc/swanctl/{private,x509,x509crl,acerts,cacerts,ocspcerts,reqs,scripts}

# 设置正确的权限
echo "6. 设置权限..."
sudo chown -R strongswan:strongswan /var/lib/strongswan /var/run/charon /var/log/strongswan
sudo chown -R strongswan:strongswan /etc/swanctl 2>/dev/null || true
sudo chmod 755 /etc/swanctl
sudo chmod 700 /etc/swanctl/private
sudo chmod 755 /etc/swanctl/x509

# 更新 systemd 服务文件
echo "7. 更新 systemd 服务文件..."
sudo tee /etc/systemd/system/strongswan-swanctl.service > /dev/null << 'EOF'
[Unit]
Description=strongSwan IPsec IKEv1/IKEv2 daemon using swanctl
After=network-online.target
Wants=network-online.target

[Service]
Type=notify
ExecStart=/usr/sbin/charon --use-syslog
ExecReload=/bin/kill -HUP $MAINPID
KillMode=mixed
Restart=on-failure
RestartSec=5s
User=strongswan
Group=strongswan
RuntimeDirectory=charon
RuntimeDirectoryMode=0755
PrivateTmp=true
NoNewPrivileges=true

[Install]
WantedBy=multi-user.target
EOF

# 重新加载 systemd
echo "8. 重新加载 systemd..."
sudo systemctl daemon-reload

# 停止并启动服务
echo "9. 重启服务..."
sudo systemctl stop strongswan-swanctl 2>/dev/null || true
sudo systemctl stop strongswan 2>/dev/null || true
sudo systemctl start strongswan-swanctl

# 检查服务状态
echo "10. 检查服务状态..."
sleep 3
if sudo systemctl is-active --quiet strongswan-swanctl; then
    echo "✅ strongSwan 服务启动成功！"
    echo ""
    echo "服务状态："
    sudo systemctl status strongswan-swanctl --no-pager -l
    echo ""
    echo "测试 swanctl 命令："
    sudo swanctl --version 2>/dev/null || echo "swanctl 命令测试失败"
else
    echo "❌ 服务启动失败，查看详细日志："
    sudo journalctl -u strongswan-swanctl --no-pager -n 30
    echo ""
    echo "检查 charon 进程："
    ps aux | grep charon | grep -v grep
fi

echo "=== 修复完成 ==="
