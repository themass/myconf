# strongSwan 6.0.2 配置文件

本目录包含 strongSwan 6.0.2 的配置文件模板，参考官方文档和 5.6.3 版本的配置方案。

## 文件说明

### 配置文件
- `strongswan.conf` - strongSwan 主配置文件
- `swanctl.conf.template` - swanctl 默认端口配置模板 (500/4500)
- `swanctl_port.conf.template` - swanctl 端口配置模板 (500/4500/8080/8081)
- `updown.sh` - 连接生命周期脚本

### 使用方法

#### 1. 部署 strongSwan 6.0.2
```bash
./vpn_setup.sh strongswan6
```

#### 2. 配置默认端口 (500/4500)
```bash
./vpn_setup.sh strongswanconf6
```

#### 3. 配置端口版本 (500/4500/8080/8081)
```bash
./vpn_setup.sh strongswanconf_port6
```

## 配置特点

### 默认端口配置
- IKE: 500/udp
- NAT-T: 4500/udp
- 支持 EAP-RADIUS 和证书认证
- IP 地址池: 10.0.0.0/24, 10.0.1.0/24

### 端口配置
- IKE: 500/udp, 8080/udp, 8081/udp
- NAT-T: 4500/udp
- 支持 EAP-RADIUS 和证书认证
- IP 地址池: 10.0.0.0/24, 10.0.1.0/24, 10.0.2.0/24, 10.0.3.0/24

## 管理命令

### 服务管理
```bash
# 启动服务
sudo ipsec start

# 停止服务
sudo ipsec stop

# 重启服务
sudo ipsec restart

# 查看状态
sudo ipsec status
```

### 连接管理
```bash
# 查看连接
sudo swanctl --list-conns

# 查看活跃连接
sudo swanctl --list-sas

# 查看证书
sudo swanctl --list-certs

# 重新加载配置
sudo swanctl --load-all
```

### 日志查看
```bash
# 查看系统日志
sudo journalctl -u strongswan-swanctl -f

# 查看 strongSwan 日志
sudo tail -f /var/log/strongswan.log

# 查看 updown 脚本日志
sudo tail -f /var/log/strongswan-updown.log
```

## 证书管理

证书通过 `caip` 函数动态生成，包括：
- CA 证书 (caCert.pem)
- 服务器证书 (serverCert.pem)
- 客户端证书 (clientCert.pem)
- PKCS12 格式客户端证书 (clientCert.p12)

## 防火墙配置

updown.sh 脚本会自动配置防火墙规则：
- 允许 IKE 和 NAT-T 端口
- 配置 NAT 规则
- 配置转发规则

## 参考文档

- [strongSwan 官方文档](https://docs.strongswan.org/docs/latest/)
- [strongSwan 安装文档](https://github.com/strongswan/strongswan/blob/master/INSTALL)
- [swanctl 配置文档](https://docs.strongswan.org/docs/latest/swanctl/swanctlConf.html)
