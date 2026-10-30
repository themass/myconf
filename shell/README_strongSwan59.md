# strongSwan 5.9.14（ipsec.conf）

默认从 **5.6.3 升级到 5.9.14**，配置仍用仓库里的 `strongswan_conf/`、`strongswan_conf_port/`（EAP-RADIUS、8081/8080），与原先 5.6.3 行为一致，兼容 OpenSSL 3。

## 一键部署（阿里云端口版，推荐）

```bash
cd ~/work/myconf && git pull
cd shell
bash vpn_setup.sh strongswan59_all
```

## 分步

```bash
bash vpn_setup.sh strongswan          # 编译 5.9.14
bash vpn_setup.sh strongswanconf_port # ipsec.conf + charon 8081/8080
bash vpn_setup.sh caip                # 证书到 /etc/ipsec.d/
bash vpn_setup.sh net                 # ip_forward
# 防火墙若已配过可跳过；否则 dev=$(ip -4 route show default | awk '/dev/{print $3;exit}')
bash vpn_setup.sh iptables            # 需传网卡时用 setup_iptables 函数所在流程
```

## 从 6.0.2 切回 5.9

6.x 的 `strongswan.service`（charon-systemd + swanctl）与 5.x 不兼容。`strongswan` 安装时会删除该 unit 并启用 **strongswan-starter** / `ipsec restart`。

```bash
sudo systemctl stop strongswan 2>/dev/null || true
bash vpn_setup.sh strongswan59_all
```

## 检查

```bash
ipsec version          # 应含 5.9.14
ipsec statusall
tail -f /var/log/charon.log
```

## 强制用 5.6.3（不推荐）

```bash
STRONGSWAN_LEGACY_VERSION=5.6.3 bash vpn_setup.sh strongswan
```
