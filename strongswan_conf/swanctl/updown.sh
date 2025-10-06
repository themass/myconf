#!/bin/bash
# strongSwan 6.0 updown 脚本
# 用于处理 VPN 连接建立和断开时的网络配置

# 设置日志文件
LOG_FILE="/var/log/strongswan-updown.log"

# 记录日志函数
log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$LOG_FILE"
}

# 获取参数
PLUTO_VERB="$1"
PLUTO_CONNECTION="$2"
PLUTO_PEER="$3"
PLUTO_PEER_ID="$4"
PLUTO_IFACE="$5"
PLUTO_ME="$6"
PLUTO_MY_CLIENT="$7"
PLUTO_OTHER_CLIENT="$8"

log_message "Updown script called: $PLUTO_VERB for connection $PLUTO_CONNECTION"

case "$PLUTO_VERB" in
    up-client)
        log_message "Client connected: $PLUTO_OTHER_CLIENT"
        # 在这里添加客户端连接时的处理逻辑
        ;;
    down-client)
        log_message "Client disconnected: $PLUTO_OTHER_CLIENT"
        # 在这里添加客户端断开时的处理逻辑
        ;;
    *)
        log_message "Unknown verb: $PLUTO_VERB"
        ;;
esac

exit 0
