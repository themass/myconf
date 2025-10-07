# strongSwan 6.0 部署脚本使用说明

## 📋 概述

本脚本新增了 strongSwan 6.0 的部署和配置功能，提供了安全优化的配置选项。

## 🆕 新增功能

### 1. strongSwan 6.0 部署函数
- `strongswan_setup_6()` - 部署 strongSwan 6.0 软件
- `strongswan_config_6()` - 配置 strongSwan 6.0 安全版本
- `strongswan_config_port_6()` - 配置 strongSwan 6.0 端口版本
- `strongswan_setup_all_6()` - 完整部署 strongSwan 6.0
- `check_vpn_6()` - 检查 strongSwan 6.0 状态

### 2. 安全优化特性
- 使用现代加密算法
- 移除不安全的配置
- 集成防火墙规则
- 增强日志和监控
- 自动证书管理

## 🚀 使用方法

### 快速部署 strongSwan 6.0
```bash
# 完整部署（推荐）
./vpn_setup.sh strongswanall6

# 分步部署
./vpn_setup.sh strongswan6      # 仅安装软件
./vpn_setup.sh strongswanconf6  # 配置安全版本
```

### 检查服务状态
```bash
# 检查 strongSwan 6.0 状态
./vpn_setup.sh check_vpn6

# 检查 strongSwan 5.6.3 状态（旧版本）
./vpn_setup.sh check_vpn
```

### 端口配置
```bash
# 配置端口版本
./vpn_setup.sh strongswanconf_port6
```

## 📊 功能对比

| 功能 | strongSwan 5.6.3 | strongSwan 6.0 |
|------|------------------|----------------|
| 部署命令 | `strongswan` | `strongswan6` |
| 配置命令 | `strongswanconf` | `strongswanconf6` |
| 检查命令 | `check_vpn` | `check_vpn6` |
| 配置文件 | `ipsec.conf` | `swanctl.conf` |
| 管理工具 | `ipsec` | `swanctl` |
| 服务名称 | `strongswan` | `strongswan-swanctl` |

## 🔧 部署流程

### 1. 完整部署流程
```bash
# 1. 安装基础软件
./vpn_setup.sh soft

# 2. 完整部署 strongSwan 6.0
./vpn_setup.sh strongswanall6

# 3. 检查部署状态
./vpn_setup.sh check_vpn6
```

### 2. 分步部署流程
```bash
# 1. 安装 strongSwan 6.0
./vpn_setup.sh strongswan6

# 2. 配置安全版本
./vpn_setup.sh strongswanconf6

# 3. 设置防火墙
./vpn_setup.sh iptables

# 4. 配置网络
./vpn_setup.sh net

# 5. 初始化证书
./vpn_setup.sh caip
```

## 📁 配置文件位置

### strongSwan 6.0 配置
- 主配置：`/etc/swanctl.conf`
- 守护进程配置：`/etc/strongswan.conf`
- 证书目录：`/etc/swanctl/x509/`
- 私钥目录：`/etc/swanctl/private/`
- 脚本目录：`/etc/swanctl/scripts/`

### 日志文件
- 系统日志：`journalctl -u strongswan-swanctl`
- 主日志：`/var/log/strongswan/charon.log`
- 安全日志：`/var/log/strongswan/security.log`
- 防火墙日志：`/var/log/strongswan/firewall.log`

## 🛠️ 管理命令

### 服务管理
```bash
# 启动服务
sudo systemctl start strongswan-swanctl

# 停止服务
sudo systemctl stop strongswan-swanctl

# 重启服务
sudo systemctl restart strongswan-swanctl

# 查看状态
sudo systemctl status strongswan-swanctl
```

### 配置管理
```bash
# 重新加载配置
sudo swanctl --load-all

# 查看连接
sudo swanctl --list-conns

# 查看活跃连接
sudo swanctl --list-sas

# 查看证书
sudo swanctl --list-certs

# 启动连接
sudo swanctl --initiate --child radius-secure

# 停止连接
sudo swanctl --terminate --child radius-secure
```

## ⚠️ 注意事项

### 1. 版本兼容性
- strongSwan 6.0 与 5.6.3 不兼容
- 配置文件格式完全不同
- 管理命令不同

### 2. 安全改进
- 移除了明文密码存储
- 使用现代加密算法
- 增强了访问控制
- 启用了安全监控

### 3. 部署建议
- 先在测试环境验证
- 备份现有配置
- 逐步迁移用户
- 监控服务状态

## 🔍 故障排除

### 常见问题
1. **服务启动失败**
   ```bash
   sudo journalctl -u strongswan-swanctl -f
   ```

2. **配置加载失败**
   ```bash
   sudo swanctl --load-all --dry-run
   ```

3. **证书问题**
   ```bash
   sudo swanctl --list-certs
   ```

4. **连接失败**
   ```bash
   sudo swanctl --list-sas
   ```

### 日志分析
```bash
# 查看实时日志
sudo journalctl -u strongswan-swanctl -f

# 查看错误日志
sudo journalctl -u strongswan-swanctl --since "1 hour ago" | grep -i error

# 查看安全日志
sudo tail -f /var/log/strongswan/security.log
```

## 📞 技术支持

如果遇到问题：
1. 查看相关日志文件
2. 检查配置文件语法
3. 验证网络连接
4. 参考官方文档
5. 联系系统管理员

---

**⚠️ 重要提醒：在生产环境部署前，请务必在测试环境中验证所有配置！**


