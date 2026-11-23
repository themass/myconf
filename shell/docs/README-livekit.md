# LiveKit 自托管（方案 B）部署与验收

日期：2026-11-23 拍板。目标：摆脱 LiveKit Cloud 额度——App 零改动（`livekit_url` 由服务端在
`/v1/voice/sessions` 下发），换的只是服务端/worker 的三个 env 指向自托管实例。

## 拓扑

```
App ── wss://livekit.ok123find.top:443 ──▶ 8.217.122.83 nginx（TLS 终结）
                                          └─http─▶ 104.160.191.87:7880（LiveKit 信令，只绑回环）
App ── WebRTC 媒体 UDP 50000-50019 ──────▶ 104.160.191.87（ICE 直连，node_ip 钉死）
App ── TURN udp 3478 ───────────────────▶ 104.160.191.87（内置 TURN，凭据自动下发；v1.13.11 必须显式配 turn.udp_port）
App ── ICE over TCP 7881 ───────────────▶ 104.160.191.87（UDP 被封时的媒体兜底）
voice worker（已在 104）────────────────▶ ws://127.0.0.1:7880（同机）
```

DNS `livekit.ok123find.top` 已解析到 8.217.122.83（2026-11-23 dig 验证）。

## 1. 104 侧安装（root 跑）

```bash
cd /home/web/work/myconf && git pull
bash shell/livekit.sh install
```

- 二进制：上游 release `v1.13.11`（amd64），装 `/home/web/opt/livekit/<ver>/`，`current` 软链可回滚。
- 配置：`/home/web/etc/livekit/config.yaml`（600，含 API 键对；重装沿用已有键，不重签）。
- 服务：systemd unit `livekit.service`，web 用户，`--bind 127.0.0.1` 只绑信令回环。
- 首次装生成的 `LIVEKIT_API_KEY/SECRET` 会打印 key（secret 只在 config.yaml）。

常用：`bash shell/livekit.sh status | restart | rotate-key`。

## 2. 安全组（云控制台，人工）

104 放行入站：`udp 50000-50019`、`tcp 7881`、`udp 7881`、`udp 7882`。
不放行 UDP 段的后果：信令通、无声——表现和 LiveKit 坏了完全一样，别先查代码。

## 3. 8.217.122.83 侧 nginx（该机的 root）

```bash
# 1) 装 vhost（内容在 conf/nginx/app-83/livekit-ok123find.conf）
cp livekit-ok123find.conf /etc/nginx/conf.d/   # 或该机既有的站点目录，与 ok123find-proxy.conf 同级
# 2) 签证书（A 记录已指向本机）
certbot certonly --webroot -w /var/www/letsencrypt -d livekit.ok123find.top
# 3) 校验并 reload
nginx -t && systemctl reload nginx
```

验证：`curl -s -o /dev/null -w '%{http_code}' https://livekit.ok123find.top/` 应 200（LiveKit 根路径）。

## 4. companion 服务端 / voice worker 切指向（104）

两个进程的 `.env` 改成：

```
LIVEKIT_URL=wss://livekit.ok123find.top
LIVEKIT_API_KEY=<config.yaml 里的 key>
LIVEKIT_API_SECRET=<config.yaml 里的 secret>
```

注意：一个变量三处消费（worker 连入、服务端建房、App 下发），必须用域名一个值；
worker 与 LiveKit 同机走域名也无碍（TLS 绕一圈 nginx，量很小）。
改完重启这两个进程——**先做完 §5 的 ICE 冒烟再切生产**，否则媒体不通会把线上通话打断。

## 5. 验收顺序（切生产前）

1. `bash shell/livekit.sh status`：active + 本机 7880 → 200。
2. 跨机信令：Mac 上 `curl https://livekit.ok123find.top/` → 200。
3. **蜂窝 ICE 测试（关键）**：手机关 Wi-Fi 走 4G/5G，装 debug 包（`companion_base_url` 指生产 API），
   进陪伴通话；判据沿用本地 runbook：`room_connect_success → local_track_published → remote_pcm_first → remote_pcm_summary maxLevel>0`。
   不通先查：安全组 UDP（最常见）→ `lk room participants`（agent 在不在）→ TURN 是否被用（logcat `turn`）。
4. 过了再改 §4 切生产；回滚 = 把两个进程 env 改回 LiveKit Cloud 值重启（App 无感）。

## 6. 已知边界

- 单节点，无 redis（进程内汇合）。将来加第二节点要配 `redis:` 块——注意 104 生产 redis 基线（uher 卡 0001_baseline）那条旧账。
- TURN/TLS（5349）未开：内置 TURN 走 node_ip 直连，LE 域名证书签不上去。国内移动网络先验证 TURN over TCP(7881) 够用再议。
- 8.217 那台 nginx 版本未确认，vhost 里没写 `http2`（信令 WS 不需要）。
- `livekit.sh` 只碰 livekit 自己：不动 8081 companion、不动 VPN 栈、不写生产库。
