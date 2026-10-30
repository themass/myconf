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

## `no IKE config found`（客户端连 8080）

日志里已有 `radius` / `radius-natt` 且 `ipsec statusall` 正常，仍报 **no IKE config found for 172.18.39.85...** 时，最常见是 **两个 charon**：6.x 的 `charon-systemd` 或旧进程占着 UDP 8080/8081，但没有 stroke 里的 `ipsec.conf`。

在 VPS 上执行：

```bash
bash ~/work/myconf/shell/vpn_setup.sh strongswan_fix59
# 或手动（你当前就是 charon-systemd 占 8080/8081）：
sudo systemctl stop strongswan
sudo systemctl disable strongswan
sudo systemctl mask strongswan
sudo pkill -9 charon-systemd
sudo systemctl enable strongswan-starter
sudo ipsec restart
sudo lsof -i UDP:8080 -i UDP:8081   # 应显示 charon 而非 charon-sy
ps aux | grep '[c]haron'              # 不应再有 /usr/sbin/charon-systemd
```

手机再连一次，同时：

```bash
sudo tail -f /var/log/charon.log
```

应出现 `looking for an IKEv2 config` 和 `found matching ike config`（`charon.conf` 里 `cfg = 2`）。若连上时 **没有任何新日志**，说明包仍被「无配置」的 charon 收走，继续查 `ss`/`lsof`。

客户端：Server **43.110.45.118**，IKE **8081**、NAT-T **8080**（或只走 8080 时需 `radius-natt` + `leftikeport=8080`）。

## 强制用 5.6.3（不推荐）

```bash
STRONGSWAN_LEGACY_VERSION=5.6.3 bash vpn_setup.sh strongswan
```
