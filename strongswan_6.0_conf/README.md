# strongSwan 6.0.2 配置文件

本目录包含 strongSwan 6.0.2 的配置文件模板，参考官方文档和 5.6.3 版本的配置方案。

## 文件说明

### 配置文件
- `strongswan.conf` - strongSwan 主配置文件（包含 EAP-RADIUS 插件配置）
- `swanctl.conf.template` - swanctl 默认配置模板，含 `{{SERVER_IP}}` 占位符
- `swanctl_port.conf.template` - 端口版 swanctl 模板
- `strongswan.service` - systemd 单元文件

#### 1. 一键部署（推荐）
```bash
cd shell
bash vpn_setup.sh strongswan6_all
```

#### 2. 分步部署
```bash
# 使用 bash 运行（推荐）
bash vpn_setup.sh strongswan6

# 或使用 sh 运行
sh vpn_setup.sh strongswan6
```

#### 2. 配置默认端口 (500/4500)
```bash
bash vpn_setup.sh strongswanconf6
bash vpn_setup.sh caip6
```

#### 3. 配置端口版本 (500/4500/8080/8081)
```bash
bash vpn_setup.sh strongswanconf_port6
bash vpn_setup.sh caip6
```

## 配置特点

### 认证方式（与 5.6.3 一致）

- 客户端 **EAP 用户名/密码** 由 **远端 RADIUS** 校验（非本机 `secrets` 用户表）
- RADIUS 在 `/etc/strongswan.conf` → `charon.plugins.eap-radius`：
  - 地址：`radius.sspacee.com`
  - 端口：`1812` / `1813`
  - 共享密钥：`FreeVPN@vpn5296`
- `swanctl` 连接 `radius`：`remote { auth = eap-radius }`，与 5.x `rightauth=eap-radius` 等价

### strongswan.conf
- 自定义端口：**8081**（IKE）、**8080**（NAT-T），与 `strongswan_conf_port` 一致
- 启用 **eap-radius** 插件（见上）

### 默认端口配置
- IKE: **8081/udp**，NAT-T: **8080/udp**
- EAP-RADIUS + 服务器证书；地址池 `10.0.0.0/24`
- 客户端账号密码在 **RADIUS** 侧管理（与 5.6.3 相同）

## 管理命令

### 服务管理
```bash
# 启动服务
sudo systemctl start strongswan

# 停止服务
sudo systemctl stop strongswan

# 重启服务
sudo systemctl restart strongswan

# 查看状态
sudo systemctl status strongswan

# 查看详细状态
sudo ipsec statusall
```

### 连接管理
```bash
# 查看连接
sudo swanctl --list-conns

# 查看活跃连接
sudo swanctl --list-sas

# 查看证书
sudo swanctl --list-certs

# 手动重新加载配置（仅在需要时使用）
sudo swanctl --load-all
```

**注意**：通常不需要手动执行 `swanctl --load-all`，因为：
- 服务重启时会自动加载配置
- 脚本会自动处理配置加载
- 只有在特殊情况下（如热重载配置）才需要手动执行

### 日志查看
```bash
# 查看 strongSwan 日志
sudo tail -f /var/log/strongswan.log

# 查看系统日志
sudo journalctl -u strongswan -f

# 查看 updown 脚本日志
sudo tail -f /var/log/strongswan-updown.log

# 查看实时状态
sudo ipsec statusall
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

## 故障排查

### 客户端一连服务器 SSH/整机像卡死

多半是编译时启用了 **kernel-libipsec**，日志里会出现 `created TUN device: ipsec0`。全隧道流量会在用户态 `ipsec0` 里转发，小 VPS 上 CPU 会瞬间打满；**5.6.3 默认走内核 XFRM，没有这个问题**。

**立刻缓解（不必重装）：** 在 `/etc/strongswan.conf` 的 `charon.plugins` 里加上 `kernel-libipsec { load = no; }`，然后：

```bash
sudo systemctl restart strongswan
sudo swanctl --load-all --noprompt
```

重启后 charon 日志里**不应再出现** `created TUN device: ipsec0`。

**长期：** `git pull` 后重新 `bash vpn_setup.sh strongswan6`（configure 已改为 `--disable-kernel-libipsec`），或至少同步本目录的 `strongswan.conf` 并 `bash vpn_setup.sh strongswanconf6`。

连接失败时同时看：`tail -f /var/log/charon.log`、`journalctl -u strongswan -f`、`top`（是否 charon 占满 CPU）。

## 参考文档

- [strongSwan 官方文档](https://docs.strongswan.org/docs/latest/)
- [Configuration Quickstart](https://docs.strongswan.org/docs/latest/config/quickstart.html)
- [strongswan.conf 配置文档](https://docs.strongswan.org/docs/latest/config/strongswanConf.html)
- [swanctl 配置文档](https://docs.strongswan.org/docs/latest/swanctl/swanctlConf.html)
- [strongSwan 安装文档](https://github.com/strongswan/strongswan/blob/master/INSTALL)
