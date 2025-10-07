#!/bin/bash
# strongSwan 6.0 防火墙规则脚本
# 为 VPN 连接提供动态防火墙规则管理

# 配置参数
IPTABLES="/sbin/iptables"
IP6TABLES="/sbin/ip6tables"
VPN_CHAIN="STRONGSWAN"
LOG_PREFIX="strongswan:"

# 记录日志
log_firewall() {
    local message="$1"
    echo "$(date '+%Y-%m-%d %H:%M:%S') [FIREWALL] $message" >> "/var/log/strongswan/firewall.log"
}

# 初始化防火墙链
init_firewall() {
    # 创建自定义链
    $IPTABLES -t filter -N $VPN_CHAIN 2>/dev/null || true
    $IP6TABLES -t filter -N $VPN_CHAIN 2>/dev/null || true
    
    # 添加链规则到 INPUT
    $IPTABLES -t filter -C INPUT -j $VPN_CHAIN 2>/dev/null || $IPTABLES -t filter -I INPUT -j $VPN_CHAIN
    $IP6TABLES -t filter -C INPUT -j $VPN_CHAIN 2>/dev/null || $IP6TABLES -t filter -I INPUT -j $VPN_CHAIN
    
    log_firewall "Firewall chains initialized"
}

# 允许客户端访问
allow_client() {
    local client_ip="$1"
    
    if [[ -z "$client_ip" ]]; then
        log_firewall "ERROR: No client IP provided for allow_client"
        return 1
    fi
    
    # IPv4 规则
    if [[ $client_ip =~ ^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$ ]]; then
        # 允许客户端访问内网
        $IPTABLES -t filter -A $VPN_CHAIN -s $client_ip -d 10.0.0.0/8 -j ACCEPT
        $IPTABLES -t filter -A $VPN_CHAIN -s $client_ip -d 172.16.0.0/12 -j ACCEPT
        $IPTABLES -t filter -A $VPN_CHAIN -s $client_ip -d 192.168.0.0/16 -j ACCEPT
        
        # 允许客户端访问互联网
        $IPTABLES -t filter -A $VPN_CHAIN -s $client_ip -j ACCEPT
        
        # 记录连接
        $IPTABLES -t filter -A $VPN_CHAIN -s $client_ip -j LOG --log-prefix "$LOG_PREFIX ALLOW: "
        
        log_firewall "Allowed access for IPv4 client: $client_ip"
    fi
    
    # IPv6 规则
    if [[ $client_ip =~ ^fec3:: ]]; then
        $IP6TABLES -t filter -A $VPN_CHAIN -s $client_ip -j ACCEPT
        $IP6TABLES -t filter -A $VPN_CHAIN -s $client_ip -j LOG --log-prefix "$LOG_PREFIX ALLOW: "
        
        log_firewall "Allowed access for IPv6 client: $client_ip"
    fi
}

# 拒绝客户端访问
deny_client() {
    local client_ip="$1"
    
    if [[ -z "$client_ip" ]]; then
        log_firewall "ERROR: No client IP provided for deny_client"
        return 1
    fi
    
    # IPv4 规则
    if [[ $client_ip =~ ^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$ ]]; then
        # 删除允许规则
        $IPTABLES -t filter -D $VPN_CHAIN -s $client_ip -d 10.0.0.0/8 -j ACCEPT 2>/dev/null || true
        $IPTABLES -t filter -D $VPN_CHAIN -s $client_ip -d 172.16.0.0/12 -j ACCEPT 2>/dev/null || true
        $IPTABLES -t filter -D $VPN_CHAIN -s $client_ip -d 192.168.0.0/16 -j ACCEPT 2>/dev/null || true
        $IPTABLES -t filter -D $VPN_CHAIN -s $client_ip -j ACCEPT 2>/dev/null || true
        $IPTABLES -t filter -D $VPN_CHAIN -s $client_ip -j LOG --log-prefix "$LOG_PREFIX ALLOW: " 2>/dev/null || true
        
        log_firewall "Denied access for IPv4 client: $client_ip"
    fi
    
    # IPv6 规则
    if [[ $client_ip =~ ^fec3:: ]]; then
        $IP6TABLES -t filter -D $VPN_CHAIN -s $client_ip -j ACCEPT 2>/dev/null || true
        $IP6TABLES -t filter -D $VPN_CHAIN -s $client_ip -j LOG --log-prefix "$LOG_PREFIX ALLOW: " 2>/dev/null || true
        
        log_firewall "Denied access for IPv6 client: $client_ip"
    fi
}

# 清理防火墙规则
cleanup_firewall() {
    # 清空自定义链
    $IPTABLES -t filter -F $VPN_CHAIN 2>/dev/null || true
    $IP6TABLES -t filter -F $VPN_CHAIN 2>/dev/null || true
    
    # 删除链引用
    $IPTABLES -t filter -D INPUT -j $VPN_CHAIN 2>/dev/null || true
    $IP6TABLES -t filter -D INPUT -j $VPN_CHAIN 2>/dev/null || true
    
    # 删除自定义链
    $IPTABLES -t filter -X $VPN_CHAIN 2>/dev/null || true
    $IP6TABLES -t filter -X $VPN_CHAIN 2>/dev/null || true
    
    log_firewall "Firewall rules cleaned up"
}

# 主处理逻辑
case "$1" in
    "init")
        init_firewall
        ;;
    "allow")
        allow_client "$2"
        ;;
    "deny")
        deny_client "$2"
        ;;
    "cleanup")
        cleanup_firewall
        ;;
    *)
        echo "Usage: $0 {init|allow|deny|cleanup} [client_ip]"
        echo "  init     - Initialize firewall chains"
        echo "  allow    - Allow access for client IP"
        echo "  deny     - Deny access for client IP"
        echo "  cleanup  - Clean up all firewall rules"
        exit 1
        ;;
esac

exit 0


