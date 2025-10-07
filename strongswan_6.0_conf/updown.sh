#!/bin/bash
# strongSwan 6.0.2 updown 脚本
# 参考官方文档: https://docs.strongswan.org/docs/latest/

# 设置环境变量
PLUTO_INTERFACE="$1"
PLUTO_VERB="$2"
PLUTO_CONNECTION="$3"
PLUTO_CONNECTION_UUID="$4"
PLUTO_UNIQUEID="$5"

# 日志函数
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') [updown] $1" >> /var/log/strongswan-updown.log
}

# 根据连接类型设置不同的网络接口
case "$PLUTO_CONNECTION" in
    ikev2-eap)
        INTERFACE="ipsec0"
        ;;
    ikev2-cert)
        INTERFACE="ipsec1"
        ;;
    ikev2-eap-8080)
        INTERFACE="ipsec2"
        ;;
    ikev2-cert-8081)
        INTERFACE="ipsec3"
        ;;
    *)
        INTERFACE="ipsec0"
        ;;
esac

log "Connection: $PLUTO_CONNECTION, Verb: $PLUTO_VERB, Interface: $INTERFACE"

case "$PLUTO_VERB" in
    up-client)
        log "Setting up client connection: $PLUTO_CONNECTION"
        # 启用 IP 转发
        echo 1 > /proc/sys/net/ipv4/ip_forward
        # 设置 NAT 规则
        iptables -t nat -A POSTROUTING -s 10.0.0.0/24 -o $PLUTO_INTERFACE -j MASQUERADE
        iptables -t nat -A POSTROUTING -s 10.0.1.0/24 -o $PLUTO_INTERFACE -j MASQUERADE
        iptables -t nat -A POSTROUTING -s 10.0.2.0/24 -o $PLUTO_INTERFACE -j MASQUERADE
        iptables -t nat -A POSTROUTING -s 10.0.3.0/24 -o $PLUTO_INTERFACE -j MASQUERADE
        # 设置转发规则
        iptables -A FORWARD -s 10.0.0.0/24 -j ACCEPT
        iptables -A FORWARD -d 10.0.0.0/24 -j ACCEPT
        iptables -A FORWARD -s 10.0.1.0/24 -j ACCEPT
        iptables -A FORWARD -d 10.0.1.0/24 -j ACCEPT
        iptables -A FORWARD -s 10.0.2.0/24 -j ACCEPT
        iptables -A FORWARD -d 10.0.2.0/24 -j ACCEPT
        iptables -A FORWARD -s 10.0.3.0/24 -j ACCEPT
        iptables -A FORWARD -d 10.0.3.0/24 -j ACCEPT
        log "Client connection setup completed"
        ;;
    down-client)
        log "Tearing down client connection: $PLUTO_CONNECTION"
        # 清理 NAT 规则
        iptables -t nat -D POSTROUTING -s 10.0.0.0/24 -o $PLUTO_INTERFACE -j MASQUERADE 2>/dev/null || true
        iptables -t nat -D POSTROUTING -s 10.0.1.0/24 -o $PLUTO_INTERFACE -j MASQUERADE 2>/dev/null || true
        iptables -t nat -D POSTROUTING -s 10.0.2.0/24 -o $PLUTO_INTERFACE -j MASQUERADE 2>/dev/null || true
        iptables -t nat -D POSTROUTING -s 10.0.3.0/24 -o $PLUTO_INTERFACE -j MASQUERADE 2>/dev/null || true
        # 清理转发规则
        iptables -D FORWARD -s 10.0.0.0/24 -j ACCEPT 2>/dev/null || true
        iptables -D FORWARD -d 10.0.0.0/24 -j ACCEPT 2>/dev/null || true
        iptables -D FORWARD -s 10.0.1.0/24 -j ACCEPT 2>/dev/null || true
        iptables -D FORWARD -d 10.0.1.0/24 -j ACCEPT 2>/dev/null || true
        iptables -D FORWARD -s 10.0.2.0/24 -j ACCEPT 2>/dev/null || true
        iptables -D FORWARD -d 10.0.2.0/24 -j ACCEPT 2>/dev/null || true
        iptables -D FORWARD -s 10.0.3.0/24 -j ACCEPT 2>/dev/null || true
        iptables -D FORWARD -d 10.0.3.0/24 -j ACCEPT 2>/dev/null || true
        log "Client connection teardown completed"
        ;;
    *)
        log "Unknown verb: $PLUTO_VERB"
        ;;
esac

exit 0
