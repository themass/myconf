#!/bin/bash
# strongSwan 6.0 安全增强版 updown 脚本
# 提供连接建立和断开时的安全网络配置

# 配置参数
LOG_FILE="/var/log/strongswan/updown.log"
SECURITY_LOG="/var/log/strongswan/security.log"
FIREWALL_RULES="/etc/swanctl/scripts/firewall-rules.sh"

# 记录日志函数
log_message() {
    local level="$1"
    local message="$2"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "$timestamp [$level] $message" >> "$LOG_FILE"
    
    # 安全相关事件记录到安全日志
    if [[ "$level" == "SECURITY" || "$level" == "WARNING" ]]; then
        echo "$timestamp [$level] $message" >> "$SECURITY_LOG"
    fi
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

# 安全验证函数
validate_connection() {
    local peer_ip="$1"
    local client_ip="$2"
    
    # 检查 IP 地址格式
    if ! [[ $peer_ip =~ ^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$ ]]; then
        log_message "ERROR" "Invalid peer IP format: $peer_ip"
        return 1
    fi
    
    # 检查客户端 IP 是否在允许的范围内
    if [[ "$client_ip" =~ ^10\.0\.0\. ]] || [[ "$client_ip" =~ ^10\.3\.0\. ]]; then
        log_message "INFO" "Client IP $client_ip is in allowed range"
        return 0
    else
        log_message "WARNING" "Client IP $client_ip is outside allowed range"
        return 1
    fi
}

# 应用防火墙规则
apply_firewall_rules() {
    local action="$1"
    local client_ip="$2"
    
    if [[ -f "$FIREWALL_RULES" ]]; then
        log_message "INFO" "Applying firewall rules: $action for $client_ip"
        bash "$FIREWALL_RULES" "$action" "$client_ip"
    else
        log_message "WARNING" "Firewall rules script not found: $FIREWALL_RULES"
    fi
}

# 监控连接状态
monitor_connection() {
    local client_ip="$1"
    local action="$2"
    
    # 记录连接统计
    echo "$(date '+%s'),$client_ip,$action" >> "/var/log/strongswan/connections.csv"
    
    # 检查连接数限制
    local active_connections=$(grep -c ",up," "/var/log/strongswan/connections.csv" 2>/dev/null || echo "0")
    if [[ $active_connections -gt 1000 ]]; then
        log_message "WARNING" "High number of active connections: $active_connections"
    fi
}

# 主处理逻辑
case "$PLUTO_VERB" in
    up-client)
        log_message "INFO" "Client connecting: $PLUTO_OTHER_CLIENT from $PLUTO_PEER"
        
        # 安全验证
        if validate_connection "$PLUTO_PEER" "$PLUTO_OTHER_CLIENT"; then
            # 应用防火墙规则
            apply_firewall_rules "allow" "$PLUTO_OTHER_CLIENT"
            
            # 监控连接
            monitor_connection "$PLUTO_OTHER_CLIENT" "up"
            
            log_message "INFO" "Client $PLUTO_OTHER_CLIENT connected successfully"
        else
            log_message "SECURITY" "Connection rejected for $PLUTO_OTHER_CLIENT from $PLUTO_PEER"
            exit 1
        fi
        ;;
        
    down-client)
        log_message "INFO" "Client disconnecting: $PLUTO_OTHER_CLIENT from $PLUTO_PEER"
        
        # 应用防火墙规则
        apply_firewall_rules "deny" "$PLUTO_OTHER_CLIENT"
        
        # 监控连接
        monitor_connection "$PLUTO_OTHER_CLIENT" "down"
        
        log_message "INFO" "Client $PLUTO_OTHER_CLIENT disconnected"
        ;;
        
    *)
        log_message "INFO" "Unknown verb: $PLUTO_VERB for connection $PLUTO_CONNECTION"
        ;;
esac

exit 0
