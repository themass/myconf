# strongSwan 6.0 脚本结构（清理后）

## 📋 核心函数

### 1. 部署函数
- `strongswan_setup_6()` - 部署 strongSwan 6.0.2
- `strongswan_setup_all_6()` - 完整部署（部署+配置+防火墙+网络）

### 2. 配置函数
- `strongswan_config_6()` - 基础配置
- `strongswan_config_port_6()` - 端口配置（8080/8081）

### 3. 辅助函数
- `copy_config_files()` - 复制配置文件
- `generate_certificates()` - 生成基础证书
- `generate_certificates_port()` - 生成端口配置证书

### 4. 防火墙函数
- `setup_iptables_6()` - 完整防火墙规则（包含8080/8081）
- `setup_iptables_simple()` - 基础防火墙规则

### 5. 网络函数
- `net()` - 网络参数配置

### 6. 工具函数
- `get_ip()` - 获取服务器IP
- `get_netdev()` - 获取网络设备

## 🗂️ 配置文件目录

```
strongswan_6.0_conf/
├── swanctl.conf.template         # 基础配置模板
├── swanctl_port.conf.template    # 端口配置模板
├── strongswan.conf                # strongswan 主配置
└── updown.sh                      # updown 脚本
```

## 🚀 使用方法

```bash
# 基础配置
./vpn_setup.sh strongswan_config6

# 端口配置
./vpn_setup.sh strongswan_config_port6

# 完整部署
./vpn_setup.sh strongswan6_all
```

## ✅ 清理完成

- ✅ 删除了所有内嵌的复杂配置生成代码
- ✅ 使用配置文件复制方式（类似5.6.3版本）
- ✅ 脚本结构清晰，函数职责明确
- ✅ 配置文件独立，易于维护
