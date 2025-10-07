# strongSwan 6.0 安全优化配置

## 📋 概述

这是从 strongSwan 5.6.3 升级到 6.0 版本的安全优化配置包。在保持原有功能的基础上，大幅提升了安全性和性能。

## 🔒 主要安全改进

### 1. 加密算法优化
- ✅ 移除所有不安全的加密套件
- ✅ 使用现代安全算法（AES-256-GCM, SHA-256, ECP-384）
- ✅ 启用 Perfect Forward Secrecy (PFS)
- ✅ 优化重密钥策略

### 2. 认证安全增强
- ✅ 移除明文密码存储
- ✅ 通过 RADIUS 服务器统一管理用户认证
- ✅ 启用 OCSP 证书状态检查
- ✅ 强制 CRL 验证

### 3. 网络安全防护
- ✅ 集成动态防火墙规则
- ✅ 客户端访问控制
- ✅ 连接状态监控
- ✅ 异常行为检测

### 4. 日志和审计
- ✅ 分离安全日志和操作日志
- ✅ 详细的安全事件记录
- ✅ 连接统计和监控
- ✅ 实时威胁检测

## 📁 目录结构

```
strongswan_6.0_optimized/
├── swanctl.conf                    # 主配置文件
├── strongswan.conf                 # 守护进程配置
├── swanctl/                        # 证书和密钥目录
│   ├── private/                    # 私钥文件
│   ├── x509/                       # 证书文件
│   └── ...                         # 其他证书目录
├── scripts/                        # 脚本目录
│   ├── updown-secure.sh           # 连接管理脚本
│   └── firewall-rules.sh          # 防火墙规则脚本
└── docs/                          # 文档目录
    ├── SECURITY_IMPROVEMENTS.md   # 安全改进说明
    └── MIGRATION_GUIDE.md         # 迁移指南
```

## 🚀 快速部署

### 1. 环境准备
```bash
# 创建必要的目录
sudo mkdir -p /var/log/strongswan
sudo mkdir -p /etc/swanctl/{private,x509,x509crl,acerts,cacerts,ocspcerts,reqs,scripts}

# 设置权限
sudo chown -R strongswan:strongswan /var/log/strongswan /etc/swanctl
```

### 2. 证书迁移
```bash
# 复制证书文件（请替换为实际路径）
sudo cp /path/to/your/certs/*.pem /etc/swanctl/x509/
sudo cp /path/to/your/private/*.pem /etc/swanctl/private/

# 设置正确的权限
sudo chmod 644 /etc/swanctl/x509/*
sudo chmod 600 /etc/swanctl/private/*
```

### 3. 配置文件部署
```bash
# 复制配置文件
sudo cp swanctl.conf /etc/swanctl.conf
sudo cp strongswan.conf /etc/strongswan.conf

# 复制脚本
sudo cp scripts/*.sh /etc/swanctl/scripts/
sudo chmod +x /etc/swanctl/scripts/*.sh
```

### 4. 服务启动
```bash
# 停止旧服务
sudo systemctl stop strongswan

# 启动新服务
sudo systemctl enable strongswan-swanctl
sudo systemctl start strongswan-swanctl
```

### 5. 配置验证
```bash
# 检查配置
sudo swanctl --load-all --dry-run

# 查看连接
sudo swanctl --list-conns

# 查看日志
sudo journalctl -u strongswan-swanctl -f
```

## ⚠️ 重要安全提醒

### 原配置的安全问题
1. **明文密码暴露** - `ipsec.secrets` 中包含明文用户密码
2. **过时加密算法** - 使用了不安全的加密套件
3. **配置错误** - 存在重复和冲突的配置项

### 必须解决的安全问题
1. **立即移除明文密码** - 通过 RADIUS 服务器管理用户认证
2. **更新过期证书** - 确保证书在有效期内
3. **检查防火墙规则** - 确保网络访问控制正确
4. **启用安全监控** - 监控异常连接和攻击行为

## 📊 性能对比

| 项目 | 原配置 (5.6.3) | 新配置 (6.0) | 改进 |
|------|---------------|-------------|------|
| 加密算法 | 混合安全级别 | 现代安全算法 | ✅ 更安全 |
| 重密钥时间 | 8小时 | 4小时 | ✅ 更频繁 |
| 日志记录 | 基础日志 | 安全审计日志 | ✅ 更详细 |
| 防火墙集成 | 无 | 动态规则 | ✅ 更灵活 |
| 监控能力 | 基础 | 全面监控 | ✅ 更完善 |

## 🔧 管理命令

### 常用管理命令
```bash
# 查看连接状态
sudo swanctl --list-sas

# 启动连接
sudo swanctl --initiate --child radius-secure

# 停止连接
sudo swanctl --terminate --child radius-secure

# 重新加载配置
sudo swanctl --load-all

# 查看证书
sudo swanctl --list-certs

# 查看日志
sudo journalctl -u strongswan-swanctl -f
```

### 防火墙管理
```bash
# 初始化防火墙
sudo /etc/swanctl/scripts/firewall-rules.sh init

# 清理防火墙规则
sudo /etc/swanctl/scripts/firewall-rules.sh cleanup
```

## 📚 文档说明

- **SECURITY_IMPROVEMENTS.md** - 详细的安全改进说明
- **MIGRATION_GUIDE.md** - 完整的迁移指南
- **README.md** - 本文件，快速入门指南

## 🆘 故障排除

### 常见问题
1. **配置加载失败** - 检查配置文件语法和权限
2. **证书问题** - 验证证书有效性和路径
3. **连接失败** - 检查 RADIUS 服务器连接
4. **防火墙问题** - 验证防火墙规则和权限

### 日志位置
- 主日志：`/var/log/strongswan/charon.log`
- 安全日志：`/var/log/strongswan/security.log`
- 防火墙日志：`/var/log/strongswan/firewall.log`
- 系统日志：`journalctl -u strongswan-swanctl`

## 📞 技术支持

如需技术支持，请：
1. 查看相关文档
2. 检查日志文件
3. 参考官方文档：https://docs.strongswan.org/
4. 联系系统管理员

---

**⚠️ 警告：在生产环境部署前，请务必在测试环境中验证所有配置！**


