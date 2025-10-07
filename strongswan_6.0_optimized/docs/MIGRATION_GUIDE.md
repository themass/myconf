# strongSwan 5.6.3 到 6.0 迁移指南

## 📁 目录结构对比

### 原配置结构 (5.6.3)
```
strongswan_conf/
├── ipsec.conf          # 连接配置
├── ipsec.secrets       # 认证配置 (包含明文密码!)
├── charon.conf         # 守护进程配置
└── strongswan.conf     # 主配置文件
```

### 新配置结构 (6.0)
```
strongswan_6.0_optimized/
├── swanctl.conf                    # 主配置文件
├── strongswan.conf                 # 守护进程配置
├── swanctl/                        # 证书和密钥目录
│   ├── private/                    # 私钥文件
│   ├── x509/                       # 证书文件
│   ├── x509crl/                    # CRL 文件
│   ├── acerts/                     # 中间证书
│   ├── cacerts/                    # CA 证书
│   ├── ocspcerts/                  # OCSP 证书
│   └── reqs/                       # 证书请求
├── scripts/                        # 脚本目录
│   ├── updown-secure.sh           # 连接管理脚本
│   └── firewall-rules.sh          # 防火墙规则脚本
└── docs/                          # 文档目录
    ├── SECURITY_IMPROVEMENTS.md   # 安全改进说明
    └── MIGRATION_GUIDE.md         # 本文件
```

## 🔄 配置迁移对照表

### 连接配置迁移

| 原配置 (ipsec.conf) | 新配置 (swanctl.conf) | 说明 |
|-------------------|---------------------|------|
| `conn radius` | `connections.radius-secure` | 重命名为更明确的名称 |
| `keyexchange=ikev2` | `version = 2` | 语法简化 |
| `ike=aes256-sha384-ecp384,...` | `proposals = aes256gcm128-sha256-ecp384,...` | 使用更安全的算法 |
| `leftauth=pubkey` | `local.auth = pubkey` | 语法更新 |
| `rightauth=eap-radius` | `remote.auth = eap-radius` | 语法更新 |
| `rightsourceip=10.0.0.0/24` | `children.radius-secure.remote_ts = 10.0.0.0/24` | 语法更新 |

### 认证配置迁移

| 原配置 (ipsec.secrets) | 新配置 | 说明 |
|----------------------|--------|------|
| `: RSA serverKey.pem` | `swanctl/private/serverKey.pem` | 移动到专用目录 |
| `usertest1 : EAP "usertest123"` | **移除** | 明文密码不安全，通过 RADIUS 管理 |
| `leftca=caCert.pem` | `authorities.ca.cacert = caCert.pem` | 语法更新 |

### 守护进程配置迁移

| 原配置 (charon.conf) | 新配置 (strongswan.conf) | 说明 |
|-------------------|----------------------|------|
| `duplicheck.enable = no` | `duplicheck.enable = no` | 保持不变 |
| `dns1 = 8.8.8.8` | `dns1 = 8.8.8.8` | 保持不变，添加更多 DNS |
| `filelog {...}` | `filelog {...}` | 增强日志配置 |

## 🚀 部署步骤

### 1. 环境准备
```bash
# 创建日志目录
sudo mkdir -p /var/log/strongswan
sudo chown strongswan:strongswan /var/log/strongswan

# 创建配置目录
sudo mkdir -p /etc/swanctl/{private,x509,x509crl,acerts,cacerts,ocspcerts,reqs}
```

### 2. 证书和密钥迁移
```bash
# 复制证书文件
sudo cp /path/to/original/certs/*.pem /etc/swanctl/x509/

# 复制私钥文件
sudo cp /path/to/original/private/*.pem /etc/swanctl/private/

# 设置正确的权限
sudo chmod 644 /etc/swanctl/x509/*
sudo chmod 600 /etc/swanctl/private/*
sudo chown -R strongswan:strongswan /etc/swanctl/
```

### 3. 配置文件部署
```bash
# 复制新配置文件
sudo cp swanctl.conf /etc/swanctl.conf
sudo cp strongswan.conf /etc/strongswan.conf

# 复制脚本文件
sudo cp scripts/*.sh /etc/swanctl/scripts/
sudo chmod +x /etc/swanctl/scripts/*.sh
```

### 4. 服务配置
```bash
# 停止旧服务
sudo systemctl stop strongswan

# 启用新服务
sudo systemctl enable strongswan-swanctl
sudo systemctl start strongswan-swanctl
```

### 5. 配置验证
```bash
# 检查配置语法
sudo swanctl --load-all --dry-run

# 查看连接配置
sudo swanctl --list-conns

# 查看证书
sudo swanctl --list-certs

# 查看日志
sudo journalctl -u strongswan-swanctl -f
```

## 🔧 命令对比

### 管理命令变化

| 原命令 (5.6.3) | 新命令 (6.0) | 说明 |
|---------------|-------------|------|
| `ipsec status` | `swanctl --list-sas` | 查看连接状态 |
| `ipsec listall` | `swanctl --list-conns` | 列出所有连接 |
| `ipsec reload` | `swanctl --load-all` | 重新加载配置 |
| `ipsec restart` | `systemctl restart strongswan-swanctl` | 重启服务 |
| `ipsec up radius` | `swanctl --initiate --child radius-secure` | 启动连接 |
| `ipsec down radius` | `swanctl --terminate --child radius-secure` | 停止连接 |

### 日志查看
```bash
# 原方式
sudo tail -f /var/log/charon.log

# 新方式
sudo journalctl -u strongswan-swanctl -f
sudo tail -f /var/log/strongswan/charon.log
sudo tail -f /var/log/strongswan/security.log
```

## ⚠️ 注意事项

### 1. 兼容性问题
- 新配置不兼容旧版本的 `ipsec` 命令
- 需要更新所有管理脚本
- 客户端配置可能需要调整

### 2. 性能考虑
- 新的加密算法可能影响性能
- 建议在测试环境验证性能
- 根据硬件能力调整配置

### 3. 安全考虑
- 移除所有明文密码
- 更新过期的证书
- 启用所有安全功能

### 4. 监控和日志
- 新日志格式需要更新监控脚本
- 增加安全日志监控
- 配置日志轮转

## 🔍 故障排除

### 常见问题及解决方案

1. **配置加载失败**
   ```bash
   # 检查配置文件语法
   sudo swanctl --load-all --dry-run
   
   # 查看详细错误信息
   sudo journalctl -u strongswan-swanctl -n 50
   ```

2. **证书问题**
   ```bash
   # 检查证书文件
   sudo swanctl --list-certs
   
   # 验证证书有效性
   openssl x509 -in /etc/swanctl/x509/serverCert.pem -text -noout
   ```

3. **连接失败**
   ```bash
   # 查看连接状态
   sudo swanctl --list-sas
   
   # 查看详细日志
   sudo tail -f /var/log/strongswan/charon.log
   ```

4. **RADIUS 认证问题**
   ```bash
   # 测试 RADIUS 连接
   radtest username password radius.sspacee.com 1812 FreeVPN@vpn5296
   
   # 查看 RADIUS 日志
   sudo tail -f /var/log/strongswan/security.log
   ```

## 📞 技术支持

如果遇到问题，请：
1. 查看相关日志文件
2. 参考官方文档：https://docs.strongswan.org/
3. 检查配置文件语法
4. 验证网络连接
5. 联系系统管理员


