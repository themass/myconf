# VPN 服务端安装脚本

统一入口 `vpn.sh`，所有协议都是 `bash vpn.sh <模块> <动作>`。服务器公网地址、出口网卡、监听地址都由脚本自动识别，识别错了才需要手动指定。

```bash
bash vpn.sh help                  # 总览
bash vpn.sh <模块> help           # 某个模块的动作和环境变量
bash vpn.sh ports                 # 各协议默认端口 + 本机监听情况
bash vpn.sh links                 # 已安装协议的客户端链接
```

## 模块与默认端口

同一台机器上可以全部装上，默认端口互不冲突。

| 模块 | 协议 | 默认端口 | 改端口的环境变量 |
|---|---|---|---|
| `strongswan` | IKEv2/IPsec（59 = 5.9 ipsec.conf，6 = 6.x swanctl） | 默认版 udp 500/4500，端口版 udp 8081/8080 | 配置文件 |
| `xray` | VLESS + Reality | tcp 443 | `XRAY_PORT` |
| `singbox` | VLESS + Reality | tcp 444 | `SB_VLESS_PORT` |
| `singbox` | Trojan | tcp 8443 | `SB_TROJAN_PORT` |
| `singbox` | VMess + WebSocket | tcp 8880 | `SB_VMESS_PORT` |
| `singbox` | Shadowsocks | tcp+udp 8388 | `SB_SS_PORT` |
| `singbox` | Hysteria2 | udp 8444 | `SB_HY2_PORT` |
| `wireguard` | WireGuard | udp 51820 | `WG_PORT` |
| `ssr` | ShadowsocksR / ss-panel | 见 `ssr_conf/` | |
| `system` | 依赖、内核参数、BBR、IPsec NAT、监控、诊断 | | |

端口被其他进程占用时脚本会停下并说明占用者，不会覆盖。云厂商的安全组需要自己在控制台放行，脚本每次结束会列出要放行的端口。

## 常用流程

```bash
# Xray VLESS+Reality（装完直接输出客户端链接）
bash vpn.sh xray install

# sing-box：一次装全部协议，或者按需添加
bash vpn.sh singbox add all
bash vpn.sh singbox add hysteria2
bash vpn.sh singbox links

# WireGuard：给 App 登记公钥，或者直接生成整套客户端配置
bash vpn.sh wireguard install
bash vpn.sh wireguard add-peer phone <客户端公钥>
bash vpn.sh wireguard add-peer laptop

# strongSwan 5.9 一键（编译 + 端口版配置 + 证书 + 防火墙 + 内核参数）
bash vpn.sh strongswan all 59
```

## 目录

```
shell/
  vpn.sh                  统一入口
  lib/common.sh           日志、地址/网卡识别、模板渲染、端口检查、防火墙
  lib/xray_reality_fields.py   读 Xray 配置里的 Reality 字段
  modules/                每个模块一个文件：system strongswan ssr xray singbox wireguard
  vpn_setup.sh            旧参数 -> vpn.sh 的转发（兼容旧的 README 和手顺）
  ssvpn_setup.sh          同上
  ipsecstatus.sh          crontab 在用（monitor/root），路径不要动
templates/                新协议的配置模板，脚本里不放配置内容
  singbox/ xray/ wireguard/ strongswan/ system/
strongswan_conf/ strongswan_conf_port/ strongswan_6.0_conf/ ssr_conf/   strongSwan、SSR 原有配置，位置不变
```

## 配置模板怎么用

模板用 `{{KEY}}` 占位。脚本渲染时把值填进去，**渲染后还有没填的占位符就直接报错**，不会把半成品配置写到服务器上。想改配置结构，改 `templates/` 下对应文件即可，不用动脚本。

- sing-box 每个协议一个 JSON，装在 `/etc/sing-box/conf.d/`，用 `-C` 目录方式合并加载；写入前会把整套配置放进临时目录用 `sing-box check` 校验，通过才生效。
- 每个协议的 UUID、密钥、密码保存在 `/etc/sing-box/state/<协议>.env`（root 才能读）。重复运行沿用，已经发出去的链接不会失效；`SB_FORCE=1` 才重新生成。
- Trojan / Hysteria2 默认生成以服务器 IP 为 SAN 的自签证书，链接里带 `insecure=1`。有域名和正式证书时：`SB_DOMAIN=example.com SB_CERT_FILE=... SB_KEY_FILE=... bash vpn.sh singbox add trojan`，注意证书私钥要让 `sing-box` 用户可读。

## 安装方式说明

- **sing-box**：下载 GitHub 发布包，版本固定在 `SB_VERSION`（默认 1.13.5，和 App 里的 libbox 一致）。
- **Xray**：下载固定版本发布包，用 `.dgst` 里的 SHA256 校验通过后才安装；不执行任何远端脚本。服务器上已经用官方脚本装过 Xray 时，二进制和 systemd 服务保持原样，只管理配置。
- **系统参数**：内核参数写入 `/etc/sysctl.d/`，文件句柄数写入 `/etc/security/limits.d/`，重复运行不会堆叠。防火墙规则先检查再追加。

## 没有搬动的

- `setup.sh start.sh root_init.sh radiusd.sh soft_setup.sh soft_setup_web.sh`：nginx / MySQL / Tomcat / Radius 等服务器基础设施脚本，不属于 VPN 安装。里面的相对路径（`../monitor`、`../radius`）依赖当前目录，没有改动。
- `ipsecstatus.sh`：被 `monitor/root` 的 crontab 调用。注意它的 `status_send` 在取不到连接数时会 `sudo reboot`，并上报到写死的地址。
