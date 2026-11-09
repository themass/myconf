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
| `wireguard` | WireGuard（内网 10.66.0.0/16） | udp 51820 | `WG_PORT` |
| `ssr` | ShadowsocksR / ss-panel | 见 `ssr_conf/` | |
| `system` | 依赖、系统升级、内核参数、BBR、IPsec NAT、监控、诊断 | | |
| `health` | 运行状况总览和日志（只读） | | |

端口被其他进程占用时脚本会停下并说明占用者，不会覆盖。云厂商的安全组需要自己在控制台放行，脚本每次结束会列出要放行的端口。

## 常用流程

```bash
# Xray VLESS+Reality（装完直接输出客户端链接）
bash vpn.sh xray install

# sing-box：一次装全部协议，或者按需添加
bash vpn.sh singbox add all
bash vpn.sh singbox add hysteria2
bash vpn.sh singbox links

# WireGuard：App 设备的公钥由后端管理，服务器每分钟自动拉取（地址规划见 docs/WIREGUARD-BACKEND.md）
bash vpn.sh wireguard install
WG_SYNC_URL=https://api.example.com/vvv/api/noapp/wg/peers.txt WG_SYNC_TOKEN=<令牌> bash vpn.sh wireguard sync-install
bash vpn.sh wireguard add-peer laptop      # 自己电脑等手工 peer，地址落在保留段 10.66.255.0/24

# strongSwan 5.9 一键（编译 + 端口版配置 + 证书 + 防火墙 + 内核参数）
bash vpn.sh strongswan all 59

# 升级系统包：先模拟，再执行。默认不换内核、不自动重启服务；full 才是 dist-upgrade
bash vpn.sh system upgrade dry-run
bash vpn.sh system upgrade

# 运行状况和日志（只读）：服务、端口、连接数、近期错误；日志默认打码 UUID 和密钥
bash vpn.sh health
bash vpn.sh health logs xray -f
```

## IKEv2 排障

**客户端连 8080 报 `no IKE config found`**：日志里已经有 `radius` / `radius-natt` 配置、`ipsec statusall` 也正常，却还报这个，最常见的原因是**同时有两个 charon**。6.x 的 `charon-systemd`（或残留的旧进程）占着 udp 8080/8081，但它没有加载 `ipsec.conf`，数据包被它收走了。

```bash
ss -lunp | grep -E ':(8080|8081) '     # 看谁占着端口：5.9 应该是 charon，6.x 是 charon-systemd
ps aux | grep '[c]haron'                # 不应同时出现两种
```

- 用 5.9：`bash vpn.sh strongswan clean force`，再 `bash vpn.sh strongswan fix 59`（会停掉并屏蔽 6.x 的 unit，启用 strongswan-starter）。
- 用 6.x：`bash vpn.sh strongswan clean force`，再 `bash vpn.sh strongswan config 6`。
- 手机再连一次，同时看日志：`bash vpn.sh health logs strongswan -f`。5.9 的日志里应出现 `looking for an IKEv2 config` 和 `found matching ike config`；连上时没有任何新日志，说明包仍被别的进程收走，继续查上面的 `ss`。
- 5.9 与 6.x 的 unit 互不兼容，来回切换要先 `clean force`。强制装旧版 5.6.3 不推荐：`STRONGSWAN_LEGACY_VERSION=5.6.3 bash vpn.sh strongswan install 59`。

## 旧脚本去哪了

| 旧脚本 | 现在 |
|---|---|
| `check.sh` | `system kernel-check` |
| `check_strongswan.sh` | `strongswan check 6` |
| `clean_strongswan_simple.sh` `cleanup_strongswan.sh` | `strongswan clean` |
| `force_clean_strongswan.sh` | `strongswan clean force` |
| `fix_strongswan_permissions.sh` | `strongswan clean`（重建目录和权限）+ `strongswan fix 6` |
| `test_minimal_strongswan.sh` | 删除：依赖的 `strongswan.conf.test` 早已不在仓库 |
| `vpn_setup_test.sh` | 删除：`vpn_setup.sh` 重构前的副本，写死了 IP，功能都在 `modules/` 里 |
| `soft_setup.sh` 的 `kernel` | `system bbr`（原来的 `setup_kernel` 只配置 BBR，下载内核的命令早就被注释掉了） |

被删的文件都在 git 历史里，取重构前的版本用 `git show 0bb0b0c9^:shell/<文件名>`。

注意：`strongswan clean` 之后规则和目录是重建的，防火墙规则由 `system iptables-ipsec` 管理，会自动装 `iptables-persistent`，重启后 NAT 不会丢。

## 目录

```
shell/
  vpn.sh                  统一入口
  lib/common.sh           日志、地址/网卡识别、模板渲染、端口检查、防火墙
  lib/xray_reality_fields.py   读 Xray 配置里的 Reality 字段
  modules/                每个模块一个文件：system strongswan ssr xray singbox wireguard health
  vpn_setup.sh            旧参数 -> vpn.sh 的转发（兼容旧的 README 和手顺）
  ssvpn_setup.sh          同上
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
