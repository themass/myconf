# strongSwan 6.0 简化部署

## 核心函数

### 1. 部署函数
```bash
# 部署 strongSwan 6.0.2
strongswan_setup_6
```

### 2. 配置函数
```bash
# 基础配置
strongswan_config_6

# 端口配置 (8080/8081)
strongswan_config_port_6
```

### 3. 完整部署
```bash
# 一键部署（包含部署+配置+防火墙+网络）
strongswan_setup_all_6
```

## 使用方法

### 方法一：分步部署
```bash
# 1. 部署
./vpn_setup.sh strongswan6

# 2. 配置
./vpn_setup.sh strongswan_config6

# 3. 端口配置（可选）
./vpn_setup.sh strongswan_config_port6
```

### 方法二：一键部署
```bash
# 完整部署
./vpn_setup.sh strongswan6_all
```

## 管理命令

```bash
# 服务管理（类似 5.6.3）
sudo ipsec start|stop|restart|status

# 连接管理
sudo swanctl --list-conns
sudo swanctl --load-all

# 查看日志
sudo journalctl -u strongswan -f
```

## 特点

- ✅ 简化启动：使用 `ipsec` 命令（与 5.6.3 相同）
- ✅ 自动配置：动态生成配置文件
- ✅ 动态证书：参考 `caip` 函数动态生成证书
- ✅ 端口支持：支持 8080/8081 端口
- ✅ 一键部署：`strongswan_setup_all_6()` 函数
- ✅ 源码编译：支持从源码编译安装

## 证书生成

配置函数会自动生成以下证书文件：
- `caCert.pem` / `caCert3.pem` - CA 证书
- `serverCert.pem` / `serverCert3.pem` - 服务器证书
- `clientCert.pem` / `clientCert3.pem` - 客户端证书
- `clientCert.p12` / `clientCert3.p12` - PKCS12 格式客户端证书

证书生成参考了原有的 `caip` 函数，使用 `ipsec pki` 命令动态生成。
