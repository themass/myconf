#!/bin/bash
# strongSwan 6.0 部署验证脚本
# 用于验证部署是否成功

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 日志函数
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# 验证服务状态
verify_service_status() {
    log_info "验证服务状态..."
    
    if systemctl is-active --quiet strongswan-swanctl; then
        log_success "strongSwan 服务正在运行"
    else
        log_error "strongSwan 服务未运行"
        return 1
    fi
    
    if systemctl is-enabled --quiet strongswan-swanctl; then
        log_success "strongSwan 服务已启用"
    else
        log_warning "strongSwan 服务未启用"
    fi
}

# 验证配置文件
verify_config_files() {
    log_info "验证配置文件..."
    
    local config_files=(
        "/etc/swanctl.conf"
        "/etc/strongswan.conf"
    )
    
    for file in "${config_files[@]}"; do
        if [ -f "$file" ]; then
            log_success "配置文件存在: $file"
            
            # 检查配置文件语法
            if [ "$file" = "/etc/swanctl.conf" ]; then
                if swanctl --load-all --dry-run >/dev/null 2>&1; then
                    log_success "swanctl.conf 语法正确"
                else
                    log_error "swanctl.conf 语法错误"
                    return 1
                fi
            fi
        else
            log_error "配置文件不存在: $file"
            return 1
        fi
    done
}

# 验证证书文件
verify_certificates() {
    log_info "验证证书文件..."
    
    local cert_files=(
        "/etc/swanctl/x509/serverCert.pem"
        "/etc/swanctl/x509/caCert.pem"
        "/etc/swanctl/private/serverKey.pem"
    )
    
    for file in "${cert_files[@]}"; do
        if [ -f "$file" ]; then
            log_success "证书文件存在: $file"
        else
            log_warning "证书文件不存在: $file"
        fi
    done
    
    # 检查证书权限
    if [ -f "/etc/swanctl/private/serverKey.pem" ]; then
        local perms=$(stat -c %a "/etc/swanctl/private/serverKey.pem")
        if [ "$perms" = "600" ]; then
            log_success "私钥文件权限正确: $perms"
        else
            log_warning "私钥文件权限不正确: $perms (应该是 600)"
        fi
    fi
}

# 验证端口监听
verify_port_listening() {
    log_info "验证端口监听..."
    
    local ports=(500 4500 8080 8081)
    
    for port in "${ports[@]}"; do
        if netstat -tulpn 2>/dev/null | grep -q ":$port "; then
            log_success "端口 $port 正在监听"
        else
            log_warning "端口 $port 未监听"
        fi
    done
}

# 验证防火墙规则
verify_firewall_rules() {
    log_info "验证防火墙规则..."
    
    local rules=(
        "INPUT.*udp.*dpt:500"
        "INPUT.*udp.*dpt:4500"
        "INPUT.*udp.*dpt:8080"
        "INPUT.*udp.*dpt:8081"
    )
    
    for rule in "${rules[@]}"; do
        if iptables -L -n | grep -qE "$rule"; then
            log_success "防火墙规则存在: $rule"
        else
            log_warning "防火墙规则不存在: $rule"
        fi
    done
}

# 验证连接配置
verify_connections() {
    log_info "验证连接配置..."
    
    if swanctl --list-conns >/dev/null 2>&1; then
        log_success "连接配置加载成功"
        
        # 显示连接列表
        echo "连接列表："
        swanctl --list-conns | sed 's/^/  /'
    else
        log_error "连接配置加载失败"
        return 1
    fi
}

# 验证日志文件
verify_log_files() {
    log_info "验证日志文件..."
    
    local log_files=(
        "/var/log/strongswan/charon.log"
        "/var/log/strongswan/security.log"
    )
    
    for file in "${log_files[@]}"; do
        if [ -f "$file" ]; then
            log_success "日志文件存在: $file"
            
            # 检查日志文件大小
            local size=$(stat -c %s "$file" 2>/dev/null || echo "0")
            if [ "$size" -gt 0 ]; then
                log_success "日志文件有内容: $size bytes"
            else
                log_warning "日志文件为空"
            fi
        else
            log_warning "日志文件不存在: $file"
        fi
    done
}

# 验证脚本文件
verify_scripts() {
    log_info "验证脚本文件..."
    
    local scripts=(
        "/etc/swanctl/scripts/updown-secure.sh"
        "/etc/swanctl/scripts/firewall-rules.sh"
    )
    
    for script in "${scripts[@]}"; do
        if [ -f "$script" ]; then
            log_success "脚本文件存在: $script"
            
            if [ -x "$script" ]; then
                log_success "脚本文件可执行"
            else
                log_warning "脚本文件不可执行"
            fi
        else
            log_warning "脚本文件不存在: $script"
        fi
    done
}

# 验证网络连通性
verify_network_connectivity() {
    log_info "验证网络连通性..."
    
    # 检查IP转发
    if [ "$(cat /proc/sys/net/ipv4/ip_forward)" = "1" ]; then
        log_success "IP转发已启用"
    else
        log_warning "IP转发未启用"
    fi
    
    # 检查DNS解析
    if nslookup google.com >/dev/null 2>&1; then
        log_success "DNS解析正常"
    else
        log_warning "DNS解析异常"
    fi
}

# 生成验证报告
generate_report() {
    local report_file="/tmp/strongswan6_verification_report_$(date +%Y%m%d_%H%M%S).txt"
    
    log_info "生成验证报告: $report_file"
    
    {
        echo "strongSwan 6.0 部署验证报告"
        echo "生成时间: $(date)"
        echo "=========================================="
        echo
        
        echo "系统信息："
        echo "  操作系统: $(lsb_release -d 2>/dev/null | cut -f2 || uname -a)"
        echo "  内核版本: $(uname -r)"
        echo "  架构: $(uname -m)"
        echo
        
        echo "服务状态："
        systemctl status strongswan-swanctl --no-pager -l
        echo
        
        echo "连接配置："
        swanctl --list-conns
        echo
        
        echo "活跃连接："
        swanctl --list-sas
        echo
        
        echo "端口监听："
        netstat -tulpn | grep -E "(500|4500|8080|8081)"
        echo
        
        echo "防火墙规则："
        iptables -L -n | grep -E "(500|4500|8080|8081)"
        echo
        
        echo "最近日志："
        journalctl -u strongswan-swanctl --no-pager -n 20
        echo
        
    } > "$report_file"
    
    log_success "验证报告已生成: $report_file"
}

# 主验证函数
main() {
    echo "=========================================="
    echo "strongSwan 6.0 部署验证"
    echo "=========================================="
    echo
    
    local verifications=(
        "verify_service_status"
        "verify_config_files"
        "verify_certificates"
        "verify_port_listening"
        "verify_firewall_rules"
        "verify_connections"
        "verify_log_files"
        "verify_scripts"
        "verify_network_connectivity"
    )
    
    local passed=0
    local total=${#verifications[@]}
    
    for verification in "${verifications[@]}"; do
        echo "运行验证: $verification"
        if $verification; then
            ((passed++))
            echo
        else
            log_error "验证失败: $verification"
            echo
        fi
    done
    
    echo "=========================================="
    echo "验证结果: $passed/$total 通过"
    echo "=========================================="
    
    if [ $passed -eq $total ]; then
        log_success "所有验证通过！strongSwan 6.0 部署成功"
    else
        log_warning "部分验证失败，请检查部署状态"
    fi
    
    # 生成报告
    generate_report
    
    return $([ $passed -eq $total ] && echo 0 || echo 1)
}

# 运行主函数
main "$@"
