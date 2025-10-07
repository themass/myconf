#!/bin/bash
# strongSwan 6.0 部署测试脚本
# 用于验证重构后的函数是否正常工作

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查系统要求
check_system_requirements() {
    log_info "检查系统要求..."
    
    # 检查操作系统
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        log_info "操作系统: $NAME $VERSION"
        if [[ "$VERSION_ID" != "18.04" ]]; then
            log_warning "建议使用 Ubuntu 18.04，当前版本: $VERSION_ID"
        fi
    else
        log_warning "无法确定操作系统版本"
    fi
    
    # 检查权限
    if [ "$EUID" -ne 0 ]; then
        log_error "请以 root 用户运行此脚本"
        exit 1
    fi
    
    # 检查网络连接
    if ! ping -c 1 8.8.8.8 >/dev/null 2>&1; then
        log_error "网络连接失败，请检查网络设置"
        exit 1
    fi
    
    log_success "系统要求检查通过"
}

# 测试函数存在性
test_functions_exist() {
    log_info "检查函数是否存在..."
    
    # 加载脚本
    source ./vpn_setup.sh
    
    # 检查函数
    local functions=(
        "strongswan_setup_6"
        "strongswan_config_6" 
        "strongswan_config_port_6"
        "strongswan_setup_all_6"
        "generate_swanctl_config"
        "generate_strongswan_config"
        "generate_swanctl_config_port"
        "setup_iptables_6"
        "check_vpn_6"
    )
    
    for func in "${functions[@]}"; do
        if declare -f "$func" >/dev/null 2>&1; then
            log_success "函数 $func 存在"
        else
            log_error "函数 $func 不存在"
            return 1
        fi
    done
    
    log_success "所有函数检查通过"
}

# 测试配置生成
test_config_generation() {
    log_info "测试配置生成..."
    
    # 创建临时目录
    local temp_dir="/tmp/strongswan_test_$$"
    mkdir -p "$temp_dir"
    cd "$temp_dir"
    
    # 模拟服务器IP
    local test_ip="192.168.1.100"
    
    # 测试配置生成函数
    if generate_swanctl_config "$test_ip" 2>/dev/null; then
        log_success "swanctl.conf 配置生成成功"
    else
        log_error "swanctl.conf 配置生成失败"
        return 1
    fi
    
    if generate_strongswan_config 2>/dev/null; then
        log_success "strongswan.conf 配置生成成功"
    else
        log_error "strongswan.conf 配置生成失败"
        return 1
    fi
    
    if generate_swanctl_config_port "$test_ip" 2>/dev/null; then
        log_success "端口配置生成成功"
    else
        log_error "端口配置生成失败"
        return 1
    fi
    
    # 清理临时目录
    cd /
    rm -rf "$temp_dir"
    
    log_success "配置生成测试通过"
}

# 测试依赖检查
test_dependencies() {
    log_info "测试依赖检查..."
    
    # 检查必要的包
    local packages=(
        "build-essential"
        "libssl-dev"
        "libgmp-dev"
        "libcurl4-openssl-dev"
        "pkg-config"
        "wget"
        "tar"
    )
    
    for package in "${packages[@]}"; do
        if dpkg -l | grep -q "^ii.*$package"; then
            log_success "包 $package 已安装"
        else
            log_warning "包 $package 未安装，将在部署时自动安装"
        fi
    done
    
    log_success "依赖检查完成"
}

# 测试网络功能
test_network_functions() {
    log_info "测试网络功能..."
    
    # 加载脚本
    source ./vpn_setup.sh
    
    # 测试IP获取
    local ip=$(get_ip)
    if [ -n "$ip" ]; then
        log_success "IP地址获取成功: $ip"
    else
        log_error "IP地址获取失败"
        return 1
    fi
    
    # 测试网络设备获取
    local dev=$(get_netdev)
    if [ -n "$dev" ]; then
        log_success "网络设备获取成功: $dev"
    else
        log_warning "网络设备获取失败，将使用默认值"
    fi
    
    log_success "网络功能测试通过"
}

# 模拟部署测试（不实际安装）
test_deployment_simulation() {
    log_info "模拟部署测试..."
    
    # 检查下载链接
    local download_url="https://download.strongswan.org/strongswan-6.0.2.tar.bz2"
    if wget --spider "$download_url" 2>/dev/null; then
        log_success "strongSwan 6.0.2 下载链接可用"
    else
        log_warning "官方下载链接不可用，将使用备用源"
    fi
    
    # 检查编译环境
    if command -v gcc >/dev/null 2>&1; then
        log_success "GCC 编译器可用"
    else
        log_warning "GCC 编译器不可用，将在部署时安装"
    fi
    
    if command -v make >/dev/null 2>&1; then
        log_success "Make 工具可用"
    else
        log_warning "Make 工具不可用，将在部署时安装"
    fi
    
    log_success "部署模拟测试通过"
}

# 主测试函数
main() {
    echo "=========================================="
    echo "strongSwan 6.0 部署测试脚本"
    echo "=========================================="
    echo
    
    local tests=(
        "check_system_requirements"
        "test_functions_exist"
        "test_config_generation"
        "test_dependencies"
        "test_network_functions"
        "test_deployment_simulation"
    )
    
    local passed=0
    local total=${#tests[@]}
    
    for test in "${tests[@]}"; do
        echo "运行测试: $test"
        if $test; then
            ((passed++))
            echo
        else
            log_error "测试失败: $test"
            echo
        fi
    done
    
    echo "=========================================="
    echo "测试结果: $passed/$total 通过"
    echo "=========================================="
    
    if [ $passed -eq $total ]; then
        log_success "所有测试通过！可以开始部署 strongSwan 6.0"
        echo
        echo "部署命令："
        echo "  ./vpn_setup.sh strongswanall6    # 完整部署"
        echo "  ./vpn_setup.sh strongswan6       # 仅安装软件"
        echo "  ./vpn_setup.sh strongswanconf6   # 仅配置"
        echo "  ./vpn_setup.sh strongswanconf_port6  # 端口配置"
        return 0
    else
        log_error "部分测试失败，请检查环境配置"
        return 1
    fi
}

# 运行主函数
main "$@"
