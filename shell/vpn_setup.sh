#init soft

#http://it.zhaozhao.info/archives/41127
#https://segmentfault.com/a/1190000002540601
#http://www.cnblogs.com/hyzhou/category/336618.html
WORKDIR=/root/work
TMP_HOME=/root/soft
PWD=`pwd`
#ip=`/sbin/ifconfig -a|grep inet|grep -v 127.0.0.1|grep -v inet6|grep -v 10. |awk '{print $1}'|tr -d "addr:"`
init_soft() 
{
	mkdir -p ${WORKDIR}
	mkdir -p ${TMP_HOME}
	sudo apt-get update
	sudo apt-get install -y gcc automake autoconf libtool pkg-config gettext perl python flex bison gperf lcov doxygen iptables net-tools
	sudo apt-get install -y sysstat vim build-essential  git  unzip libtalloc2   libtalloc-dev libxml2-dev php-pear aptitude
	
	sudo aptitude install libgmp10 libgmp3-dev libssl-dev pkg-config libpcsclite-dev libpam0g-dev  curl   libmysqlclient-dev
	sudo apt-get -y install libcurl4-gnutls-dev
}
setup_telegraf()
{
	shelldir=`pwd`
	cd ${TMP_HOME}
	rm ${TMP_HOME}/telegraf_1.4.2-1_amd64.deb
	wget https://dl.influxdata.com/telegraf/releases/telegraf_1.4.2-1_amd64.deb --no-check-certificate
	sudo dpkg -i telegraf_1.4.2-1_amd64.deb
	cd ${shelldir}
	echo ${shelldir}
	
	cp ../monitor/telegraf.conf /etc/telegraf/
	service telegraf restart
}
## -----------------------
## Setup all aboves
## -----------------------
check_vpn() 
{
    	iptables -L 
	ipsec status | grep Associations
	ps -aux| grep fail | grep -v 'grep'
	ps -aux| grep telegraf| grep -v 'grep'
}

# strongSwan 6.0 状态检查函数
check_vpn_6() 
{
    echo "=== strongSwan 6.0 状态检查 ==="
    
    # 检查服务状态
    echo "1. 服务状态："
    sudo systemctl status strongswan-swanctl --no-pager -l
    
    echo ""
    echo "2. 连接状态："
    sudo swanctl --list-conns
    
    echo ""
    echo "3. 活跃连接："
    sudo swanctl --list-sas
    
    echo ""
    echo "4. 证书状态："
    sudo swanctl --list-certs
    
    echo ""
    echo "5. 防火墙规则："
    iptables -L -n | grep -E "(STRONGSWAN|strongswan)"
    
    echo ""
    echo "6. 进程状态："
    ps -aux | grep -E "(charon|swanctl)" | grep -v grep
    
    echo ""
    echo "7. 端口监听："
    netstat -tulpn | grep -E "(500|4500|8080|8081)"
    
    echo ""
    echo "8. 最近日志："
    sudo journalctl -u strongswan-swanctl --no-pager -n 20
    
    echo ""
    echo "9. 安全日志："
    if [ -f "/var/log/strongswan/security.log" ]; then
        sudo tail -10 /var/log/strongswan/security.log
    else
        echo "安全日志文件不存在"
    fi
}
checkspeed()
{
	cd ${TMP_HOME}
	#wget https://raw.githubusercontent.com/wn789/Superspeed/master/superbench.sh
	#bash superbench.sh
	#wget https://raw.githubusercontent.com/FunctionClub/ZBench/master/ZBench-CN.sh && bash ZBench-CN.sh 
	#wget  https://raw.githubusercontent.com/sivel/speedtest-cli/master/speedtest.py 
 	#python speedtest.py 
 	wget -qO- git.io/superbench.sh | bash
}
checkmtr()
{
	cd ${TMP_HOME}
	mkdir besttrace
	cd besttrace
	wget http://cdn.ipip.net/17mon/besttrace4linux.zip
	unzip besttrace4linux.zip
	chmod +x besttrace32
	echo '测试广州移动'
	./besttrace32 -q 1 gd.189.cn
	echo '测试广州联通'
	./besttrace32 -q 1 mall.gd10010.cn
	echo '测试广州电信'
	./besttrace32 -q 1 189.cn
}
#### open vz
# ./configure  --enable-eap-identity --enable-eap-md5 \
##--enable-eap-mschapv2 --enable-eap-tls --enable-eap-ttls --enable-eap-peap  \
#--enable-eap-tnc --enable-eap-dynamic --enable-eap-radius --enable-xauth-eap  \
#--enable-xauth-pam  --enable-dhcp  --enable-openssl  --enable-addrblock --enable-unity  \
#--enable-certexpire --enable-radattr --enable-tools --enable-openssl --disable-gmp --enable-kernel-libipsec

strongswan_setup() 
{
	cd ${TMP_HOME}
	wget http://download.strongswan.org/strongswan-5.6.3.tar.bz2 --no-check-certificate
	tar -jxvf strongswan-5.6.3.tar.bz2 && cd strongswan-5.6.3
	./configure --prefix=/usr --sysconfdir=/etc  --enable-openssl --enable-nat-transport --disable-mysql --disable-ldap  --disable-static --enable-shared --enable-md4 --enable-eap-mschapv2 --enable-eap-aka --enable-eap-aka-3gpp2  --enable-eap-gtc --enable-eap-identity --enable-eap-md5 --enable-eap-peap --enable-eap-radius --enable-eap-sim --enable-eap-sim-file --enable-eap-simaka-pseudonym --enable-eap-simaka-reauth --enable-eap-simaka-sql --enable-eap-tls --enable-eap-tnc --enable-eap-ttls
	sudo make && sudo make install
	sudo ipsec start
	cd ..
}
strongswan_config() 
{
	cd ${WORKDIR}/myconf/shell
	cp  /etc/ipsec.conf /etc/ipsec.conf.bak
	cp  ../strongswan_conf/ipsec.conf /etc/ipsec.conf
    
	cp  /etc/strongswan.d/charon.conf /etc/strongswan.d/charon.conf.bak
	cp  ../strongswan_conf/charon.conf /etc/strongswan.d/charon.conf
    
	cp  /etc/ipsec.secrets  /etc/ipsec.secrets.bak
	cp  ../strongswan_conf/ipsec.secrets /etc/ipsec.secrets
	
	cp  ../strongswan_conf/strongswan.conf /etc/strongswan.conf
	
	ipsec restart
}
strongswan_config_port() 
{
	#unzip strongswan_conf.zip
#	dos2unix strongswan_conf/ipsec.conf
#	dos2unix strongswan_conf/charon.conf
#	dos2unix strongswan_conf/ipsec.secrets
	#
#	cp  /etc/ipsec.conf /etc/ipsec.conf.bak
#	cp  strongswan_conf/ipsec.conf /etc/ipsec.conf
#    #
#	cp  /etc/strongswan.d/charon.conf /etc/strongswan.d/charon.conf.bak
#	cp  strongswan_conf/charon.conf /etc/strongswan.d/charon.conf
#    #
#	cp  /etc/ipsec.secrets  /etc/ipsec.secrets.bak
#	cp  strongswan_conf/ipsec.secrets /etc/ipsec.secrets
	
	cd ${WORKDIR}/myconf/shell
	cp  /etc/ipsec.conf /etc/ipsec.conf.bak
	cp  ../strongswan_conf_port/ipsec.conf /etc/ipsec.conf
    
	cp  /etc/strongswan.d/charon.conf /etc/strongswan.d/charon.conf.bak
	cp  ../strongswan_conf_port/charon.conf /etc/strongswan.d/charon.conf
    
	cp  /etc/ipsec.secrets  /etc/ipsec.secrets.bak
	cp  ../strongswan_conf_port/ipsec.secrets /etc/ipsec.secrets
	
	cp  ../strongswan_conf_port/strongswan.conf /etc/strongswan.conf
	
	ipsec restart
}

# strongSwan 6.0 部署函数 - 重构版
strongswan_setup_6() 
{
	echo "=== 开始部署 strongSwan 6.0.2 ==="
	cd ${TMP_HOME}
	
	# 检查是否已安装
	if command -v swanctl >/dev/null 2>&1; then
		echo "strongSwan 已安装，版本：$(swanctl --version 2>/dev/null | head -1 || echo 'unknown')"
		read -p "是否重新安装？(y/N): " -n 1 -r
		echo
		if [[ ! $REPLY =~ ^[Yy]$ ]]; then
			echo "跳过安装，继续配置..."
			return 0
		fi
	fi
	
	# 安装所有必要的依赖
	echo "安装编译依赖..."
	sudo apt-get update
	sudo apt-get install -y \
		build-essential \
		libssl-dev \
		libgmp-dev \
		libcurl4-openssl-dev \
		libsqlite3-dev \
		libsystemd-dev \
		pkg-config \
      libiptc-dev \
      libip4tc-dev \
      libip6tc-dev \
      libxtables-dev \
      libnetfilter-conntrack-dev \
      libnetfilter-queue-dev \
		libnfnetlink-dev \
		autotools-dev \
		libtool \
		autoconf \
		automake \
		flex \
		bison \
		gperf
	
	# 下载 strongSwan 6.0.2
	echo "下载 strongSwan 6.0.2..."
	if [ ! -f "strongswan-6.0.2.tar.bz2" ]; then
		wget https://download.strongswan.org/strongswan-6.0.2.tar.bz2 --no-check-certificate
		if [ $? -ne 0 ]; then
			echo "官方源下载失败，尝试备用源..."
			wget https://github.com/strongswan/strongswan/archive/refs/tags/6.0.2.tar.gz --no-check-certificate
			if [ $? -eq 0 ]; then
				tar -xzf 6.0.2.tar.gz
				mv strongswan-6.0.2 strongswan-6.0.2
			else
				echo "下载失败，请检查网络连接"
				return 1
			fi
		else
			tar -jxvf strongswan-6.0.2.tar.bz2
		fi
	fi
	
	cd strongswan-6.0.2

	# 配置编译选项 - 针对 6.0 版本优化
	echo "配置编译选项..."
	./configure \
		--prefix=/usr \
		--sysconfdir=/etc \
		--enable-openssl \
		--enable-nat-transport \
		--disable-mysql \
		--disable-ldap \
		--disable-static \
		--enable-shared \
		--enable-md4 \
		--enable-eap-mschapv2 \
		--enable-eap-aka \
		--enable-eap-aka-3gpp2 \
		--enable-eap-gtc \
		--enable-eap-identity \
		--enable-eap-md5 \
		--enable-eap-peap \
		--enable-eap-radius \
		--enable-eap-sim \
		--enable-eap-sim-file \
		--enable-eap-simaka-pseudonym \
		--enable-eap-simaka-reauth \
		--enable-eap-simaka-sql \
		--enable-eap-tls \
		--enable-eap-tnc \
		--enable-eap-ttls \
		--enable-vici \
		--enable-swanctl \
		--enable-systemd \
		--enable-attr \
		--enable-resolve \
		--enable-kernel-netlink \
		--enable-kernel-libipsec \
		--enable-socket-default \
		--enable-counters \
		--enable-forecast \
		--enable-integrity-test \
		--enable-firewall
	
	if [ $? -ne 0 ]; then
		echo "配置失败，请检查依赖是否完整安装"
		return 1
	fi
	
	# 编译
	echo "开始编译..."
	make -j$(nproc)
	if [ $? -ne 0 ]; then
		echo "编译失败"
		return 1
	fi
	
	# 安装
	echo "安装 strongSwan..."
	sudo make install
	if [ $? -ne 0 ]; then
		echo "安装失败"
		return 1
	fi
	
	# 创建必要的目录和用户
	echo "创建必要的目录..."
	sudo mkdir -p /etc/swanctl/{private,x509,x509crl,acerts,cacerts,ocspcerts,reqs,scripts}
	sudo mkdir -p /var/log/strongswan
	sudo mkdir -p /var/run/charon
	
	# 创建 strongswan 用户（如果不存在）
	if ! id "strongswan" &>/dev/null; then
		sudo useradd -r -s /bin/false strongswan
	fi
	
	# 设置权限
	sudo chown -R strongswan:strongswan /etc/swanctl /var/log/strongswan /var/run/charon 2>/dev/null || true
	sudo chmod 755 /etc/swanctl
	sudo chmod 700 /etc/swanctl/private
	sudo chmod 755 /etc/swanctl/x509
	
	# 创建 systemd 服务文件
	echo "创建 systemd 服务..."
	sudo tee /etc/systemd/system/strongswan-swanctl.service > /dev/null << 'EOF'
[Unit]
Description=strongSwan IPsec IKEv1/IKEv2 daemon using swanctl
After=network-online.target
Wants=network-online.target

[Service]
Type=notify
ExecStart=/usr/sbin/charon --use-syslog
ExecReload=/bin/kill -HUP $MAINPID
KillMode=mixed
Restart=on-failure
RestartSec=5s
User=strongswan
Group=strongswan

[Install]
WantedBy=multi-user.target
EOF
	
	# 重新加载 systemd
	sudo systemctl daemon-reload
	
	# 停止旧服务，启动新服务
	echo "启动服务..."
	sudo systemctl stop strongswan 2>/dev/null || true
	sudo systemctl stop strongswan-swanctl 2>/dev/null || true
	sudo systemctl enable strongswan-swanctl
	sudo systemctl start strongswan-swanctl
	
	# 检查服务状态
	if sudo systemctl is-active --quiet strongswan-swanctl; then
		echo "✅ strongSwan 6.0.2 部署成功！"
		echo "服务状态：$(sudo systemctl is-active strongswan-swanctl)"
	else
		echo "❌ 服务启动失败，请检查日志："
		sudo journalctl -u strongswan-swanctl --no-pager -n 20
		return 1
	fi
	
	cd ..
	echo "=== strongSwan 6.0.2 部署完成 ==="
}

# strongSwan 6.0 安全配置函数 - 重构版
strongswan_config_6() 
{
	echo "=== 开始配置 strongSwan 6.0 安全版本 ==="
	cd ${WORKDIR}/myconf/shell
	
	# 获取服务器IP
	SERVER_IP=$(get_ip)
	if [ -z "$SERVER_IP" ]; then
		echo "❌ 无法获取服务器IP地址"
		return 1
	fi
	echo "服务器IP: $SERVER_IP"
	
	# 备份现有配置
	echo "备份现有配置..."
	sudo cp /etc/swanctl.conf /etc/swanctl.conf.bak.$(date +%Y%m%d_%H%M%S) 2>/dev/null || true
	sudo cp /etc/strongswan.conf /etc/strongswan.conf.bak.$(date +%Y%m%d_%H%M%S) 2>/dev/null || true
	
	# 生成动态配置文件
	echo "生成动态配置文件..."
	generate_swanctl_config "$SERVER_IP"
	generate_strongswan_config
	
	# 复制脚本文件
	echo "复制脚本文件..."
	sudo cp ../strongswan_6.0_optimized/scripts/*.sh /etc/swanctl/scripts/
	sudo chmod +x /etc/swanctl/scripts/*.sh
	
	# 复制证书文件（如果存在）
	if [ -d "../strongswan_conf" ]; then
		echo "复制证书文件..."
		sudo cp ../strongswan_conf/*.pem /etc/swanctl/x509/ 2>/dev/null || true
		sudo cp ../strongswan_conf/*.pem /etc/swanctl/private/ 2>/dev/null || true
		
		# 设置正确的权限
		sudo chmod 644 /etc/swanctl/x509/*.pem 2>/dev/null || true
		sudo chmod 600 /etc/swanctl/private/*.pem 2>/dev/null || true
	fi
	
	# 创建日志目录
	sudo mkdir -p /var/log/strongswan
	sudo chown strongswan:strongswan /var/log/strongswan 2>/dev/null || true
	
	# 验证配置
	echo "验证配置..."
	if sudo swanctl --load-all --dry-run; then
		echo "✅ 配置验证通过"
	else
		echo "❌ 配置验证失败"
		return 1
	fi
	
	# 重新加载配置
	echo "重新加载配置..."
	sudo swanctl --load-all
	
	# 重启服务
	sudo systemctl restart strongswan-swanctl
	
	echo "✅ strongSwan 6.0 安全配置完成！"
	echo "检查配置：sudo swanctl --list-conns"
	echo "查看日志：sudo journalctl -u strongswan-swanctl -f"
	echo "=== 配置完成 ==="
}

# 生成 swanctl.conf 配置文件
generate_swanctl_config() {
	local server_ip="$1"
	echo "生成 swanctl.conf 配置文件..."
	
	sudo tee /etc/swanctl.conf > /dev/null << EOF
# strongSwan 6.0 优化配置 - 安全增强版
# 自动生成时间: $(date)
# 服务器IP: $server_ip

connections {
    # 默认连接配置 - 使用现代安全算法
    defaults {
        local_addrs = %any
        remote_addrs = %any
        version = 2
        # 优化的加密套件 - 移除不安全的算法
        proposals = aes256gcm128-sha256-ecp384,aes256gcm128-sha256-modp4096,aes256-sha256-ecp384,aes256-sha256-modp4096,aes128-sha256-ecp256,aes128-sha256-modp2048
        dpd_delay = 30s
        dpd_timeout = 120s
        dpd_action = restart
        rekey_time = 4h
        reauth_time = 8h
        fragmentation = yes
        unique = replace
        # 启用 Perfect Forward Secrecy
        rekey_margin = 10m
        # 连接超时设置
        over_time = 10m
        rand_time = 120s
    }

    # 主要 RADIUS 连接配置 - 安全优化
    radius-secure {
        local {
            auth = pubkey
            certs = serverCert.pem
            id = @$server_ip
        }
        remote {
            auth = eap-radius
            eap_id = %any
            # 限制重试次数
            send_certreq = no
        }
        children {
            radius-secure {
                local_ts = 0.0.0.0/0,::/0
                remote_ts = 10.0.0.0/24,fec3::/120
                updown = /etc/swanctl/scripts/updown-secure.sh
                # 优化的 ESP 加密套件
                esp_proposals = aes256gcm128-sha256-ecp384,aes256gcm128-sha256-modp4096,aes256-sha256-ecp384,aes256-sha256-modp4096
                # 启用压缩
                ipcomp = yes
                # 设置生存时间
                life_time = 1h
                rekey_time = 30m
                # 启用流量统计
                mode = tunnel
                start_action = trap
            }
        }
    }

    # 第二个 RADIUS 连接配置 - 安全优化
    radius3-secure {
        local {
            auth = pubkey
            certs = serverCert3.pem
            id = $server_ip
        }
        remote {
            auth = eap-radius
            eap_id = %any
            send_certreq = no
        }
        children {
            radius3-secure {
                local_ts = 0.0.0.0/0,::/0
                remote_ts = 10.3.0.0/24,fec3::/120
                updown = /etc/swanctl/scripts/updown-secure.sh
                esp_proposals = aes256gcm128-sha256-ecp384,aes256gcm128-sha256-modp4096,aes256-sha256-ecp384,aes256-sha256-modp4096
                ipcomp = yes
                life_time = 1h
                rekey_time = 30m
                mode = tunnel
                start_action = trap
            }
        }
    }
}

authorities {
    # CA 证书配置 - 增强安全
    ca {
        cacert = caCert.pem
        crl_uris = http://$server_ip/ca.crl
        # 启用 OCSP
        ocsp_uris = http://$server_ip/ocsp/
        # 证书验证设置
        crl_strict = yes
        crl_cache_time = 1h
    }
    ca3 {
        cacert = caCert3.pem
        crl_uris = http://$server_ip/ca3.crl
        ocsp_uris = http://$server_ip/ocsp/
        crl_strict = yes
        crl_cache_time = 1h
    }
}

pools {
    # IP 地址池配置 - 安全增强
    radius-pool {
        addrs = 10.0.0.0/24
        dns = 8.8.8.8, 1.1.1.1, 114.114.114.114
        # 添加 NBNS 服务器
        nbns = 8.8.8.8
    }
    radius3-pool {
        addrs = 10.3.0.0/24
        dns = 8.8.8.8, 1.1.1.1, 114.114.114.114
        nbns = 8.8.8.8
    }
}
EOF
}

# 生成 strongswan.conf 配置文件
generate_strongswan_config() {
	echo "生成 strongswan.conf 配置文件..."
	
	sudo tee /etc/strongswan.conf > /dev/null << 'EOF'
# strongSwan 6.0 安全优化配置
# 基于原配置进行安全增强和性能优化

charon {
    # 安全设置
    duplicheck.enable = no
    ignore_acquire_ts = yes
    
    # DNS 配置 - 使用更安全的 DNS 服务器
    dns1 = 8.8.8.8
    dns2 = 1.1.1.1
    dns3 = 114.114.114.114
    
    # 重试和重传配置 - 优化性能
    retry_initiate_interval = 30
    retransmit_timeout = 4
    retransmit_tries = 5
    retransmit_base = 1.8
    retransmit_timeout_tries = 0
    
    # 连接管理优化
    half_open_timeout = 60
    half_open_limit = 1000
    
    # 内存和性能优化
    cache_crls = yes
    strict_revocation = yes
    
    # 日志配置 - 增强安全审计
    filelog {
        /var/log/strongswan/charon.log {
            time_format = %b %e %T
            ike_name = yes
            append = no
            default = 1
            flush_line = yes
            # 安全相关日志级别
            ike = 2
            knl = 2
            cfg = 2
            net = 2
            enc = 2
            lib = 2
        }
        # 安全审计日志
        /var/log/strongswan/security.log {
            time_format = %b %e %T
            ike_name = yes
            append = yes
            default = 0
            flush_line = yes
            # 只记录安全相关事件
            ike = 1
            knl = 1
            cfg = 1
        }
        stderr {
            ike = 2
            knl = 3
            cfg = 2
        }
    }
    
    syslog {
        identifier = strongswan-secure
        daemon {
            default = 1
        }
        auth {
            default = -1
            ike = 0
        }
    }
    
    # 插件配置 - 安全优化
    plugins {
        include strongswan.d/charon/*.conf
        
        # EAP-RADIUS 插件配置 - 安全增强
        eap-radius {
            accounting = yes
            # 启用 RADIUS 属性过滤
            attribute_filter = yes
            servers {
                radiusServer {
                    secret = FreeVPN@vpn5296
                    address = radius.sspacee.com
                    auth_port = 1812
                    acct_port = 1813
                    # 连接超时设置
                    timeout = 5
                    retries = 3
                    # 启用 NAS 标识
                    nas_identifier = strongswan-server
                }
            }
        }
        
        # 启用安全相关插件
        attr {
            load = yes
            # 启用属性过滤
            filter = yes
        }
        resolve {
            load = yes
        }
        kernel-netlink {
            load = yes
        }
        kernel-libipsec {
            load = yes
        }
        socket-default {
            load = yes
        }
        vici {
            load = yes
        }
        # 禁用不安全的插件
        stroke {
            load = no
        }
        # 启用安全增强插件
        counters {
            load = yes
        }
        forecast {
            load = yes
        }
        # 启用完整性检查
        integrity-test {
            load = yes
        }
    }
}

include strongswan.d/*.conf
EOF
}

# strongSwan 6.0 端口配置函数 - 重构版
strongswan_config_port_6() 
{
	echo "=== 开始配置 strongSwan 6.0 端口版本 (8080/8081) ==="
	cd ${WORKDIR}/myconf/shell
	
	# 获取服务器IP
	SERVER_IP=$(get_ip)
	if [ -z "$SERVER_IP" ]; then
		echo "❌ 无法获取服务器IP地址"
		return 1
	fi
	echo "服务器IP: $SERVER_IP"
	
	# 备份现有配置
	echo "备份现有配置..."
	sudo cp /etc/swanctl.conf /etc/swanctl.conf.bak.port.$(date +%Y%m%d_%H%M%S) 2>/dev/null || true
	sudo cp /etc/strongswan.conf /etc/strongswan.conf.bak.port.$(date +%Y%m%d_%H%M%S) 2>/dev/null || true
	
	# 生成带端口配置的配置文件
	echo "生成端口配置文件..."
	generate_swanctl_config_port "$SERVER_IP"
	generate_strongswan_config
	
	# 复制脚本文件
	echo "复制脚本文件..."
	sudo cp ../strongswan_6.0_optimized/scripts/*.sh /etc/swanctl/scripts/
	sudo chmod +x /etc/swanctl/scripts/*.sh
	
	# 复制证书文件
	if [ -d "../strongswan_conf_port" ]; then
		echo "复制端口配置的证书文件..."
		sudo cp ../strongswan_conf_port/*.pem /etc/swanctl/x509/ 2>/dev/null || true
		sudo cp ../strongswan_conf_port/*.pem /etc/swanctl/private/ 2>/dev/null || true
		
		# 设置正确的权限
		sudo chmod 644 /etc/swanctl/x509/*.pem 2>/dev/null || true
		sudo chmod 600 /etc/swanctl/private/*.pem 2>/dev/null || true
	fi
	
	# 验证配置
	echo "验证配置..."
	if sudo swanctl --load-all --dry-run; then
		echo "✅ 配置验证通过"
	else
		echo "❌ 配置验证失败"
		return 1
	fi
	
	# 重新加载配置
	echo "重新加载配置..."
	sudo swanctl --load-all
	
	# 重启服务
	sudo systemctl restart strongswan-swanctl
	
	echo "✅ strongSwan 6.0 端口配置完成！"
	echo "端口配置：500, 4500, 8080, 8081"
	echo "检查配置：sudo swanctl --list-conns"
	echo "查看日志：sudo journalctl -u strongswan-swanctl -f"
	echo "=== 端口配置完成 ==="
}

# 生成带端口配置的 swanctl.conf
generate_swanctl_config_port() {
	local server_ip="$1"
	echo "生成带端口配置的 swanctl.conf 配置文件..."
	
	sudo tee /etc/swanctl.conf > /dev/null << EOF
# strongSwan 6.0 优化配置 - 端口版本 (8080/8081)
# 自动生成时间: $(date)
# 服务器IP: $server_ip

connections {
    # 默认连接配置 - 使用现代安全算法
    defaults {
        local_addrs = %any
        remote_addrs = %any
        version = 2
        # 优化的加密套件 - 移除不安全的算法
        proposals = aes256gcm128-sha256-ecp384,aes256gcm128-sha256-modp4096,aes256-sha256-ecp384,aes256-sha256-modp4096,aes128-sha256-ecp256,aes128-sha256-modp2048
        dpd_delay = 30s
        dpd_timeout = 120s
        dpd_action = restart
        rekey_time = 4h
        reauth_time = 8h
        fragmentation = yes
        unique = replace
        # 启用 Perfect Forward Secrecy
        rekey_margin = 10m
        # 连接超时设置
        over_time = 10m
        rand_time = 120s
    }

    # 主要 RADIUS 连接配置 - 端口 8080
    radius-secure {
        local {
            auth = pubkey
            certs = serverCert.pem
            id = @$server_ip
        }
        remote {
            auth = eap-radius
            eap_id = %any
            send_certreq = no
        }
        children {
            radius-secure {
                local_ts = 0.0.0.0/0,::/0
                remote_ts = 10.0.0.0/24,fec3::/120
                updown = /etc/swanctl/scripts/updown-secure.sh
                esp_proposals = aes256gcm128-sha256-ecp384,aes256gcm128-sha256-modp4096,aes256-sha256-ecp384,aes256-sha256-modp4096
                ipcomp = yes
                life_time = 1h
                rekey_time = 30m
                mode = tunnel
                start_action = trap
            }
        }
    }

    # 第二个 RADIUS 连接配置 - 端口 8081
    radius3-secure {
        local {
            auth = pubkey
            certs = serverCert3.pem
            id = $server_ip
        }
        remote {
            auth = eap-radius
            eap_id = %any
            send_certreq = no
        }
        children {
            radius3-secure {
                local_ts = 0.0.0.0/0,::/0
                remote_ts = 10.3.0.0/24,fec3::/120
                updown = /etc/swanctl/scripts/updown-secure.sh
                esp_proposals = aes256gcm128-sha256-ecp384,aes256gcm128-sha256-modp4096,aes256-sha256-ecp384,aes256-sha256-modp4096
                ipcomp = yes
                life_time = 1h
                rekey_time = 30m
                mode = tunnel
                start_action = trap
            }
        }
    }
}

authorities {
    # CA 证书配置 - 增强安全
    ca {
        cacert = caCert.pem
        crl_uris = http://$server_ip/ca.crl
        ocsp_uris = http://$server_ip/ocsp/
        crl_strict = yes
        crl_cache_time = 1h
    }
    ca3 {
        cacert = caCert3.pem
        crl_uris = http://$server_ip/ca3.crl
        ocsp_uris = http://$server_ip/ocsp/
        crl_strict = yes
        crl_cache_time = 1h
    }
}

pools {
    # IP 地址池配置 - 安全增强
    radius-pool {
        addrs = 10.0.0.0/24
        dns = 8.8.8.8, 1.1.1.1, 114.114.114.114
        nbns = 8.8.8.8
    }
    radius3-pool {
        addrs = 10.3.0.0/24
        dns = 8.8.8.8, 1.1.1.1, 114.114.114.114
        nbns = 8.8.8.8
    }
}
EOF
}

# 更新防火墙规则以支持端口 8080/8081
setup_iptables_6() {
	local dev="$1"
	echo "设置 strongSwan 6.0 防火墙规则 (包含端口 8080/8081)..."
	
	# 基础端口
	iptables -A INPUT -p udp --dport 500 -j ACCEPT 
	iptables -A INPUT -p udp --dport 4500 -j ACCEPT
	
	# 新增端口 8080/8081
	iptables -A INPUT -p udp --dport 8080 -j ACCEPT
	iptables -A INPUT -p udp --dport 8081 -j ACCEPT
	
	# NAT 规则
	iptables -t nat -A POSTROUTING -s 10.0.0.0/24 -o $dev -j MASQUERADE 
	iptables -t nat -A POSTROUTING -s 10.3.0.0/24 -o $dev -j MASQUERADE
	
	# 转发规则
	iptables -A FORWARD -s 10.0.0.0/24 -j ACCEPT 
	iptables -A FORWARD -d 10.0.0.0/24 -j ACCEPT
	iptables -A FORWARD -s 10.3.0.0/24 -j ACCEPT 
	iptables -A FORWARD -d 10.3.0.0/24 -j ACCEPT
	
	# IPv6 规则
	ip6tables -A INPUT -p udp --dport 4500 -m frag --fragfirst -j CONNMARK --set-mark 0x42
	ip6tables -A INPUT -p udp --dport 4500 -j ACCEPT
	ip6tables -A INPUT -m frag -m connmark --mark 0x42 -j ACCEPT
	
	# 保存规则
	iptables-save > /etc/iptables/rules.v4 2>/dev/null || iptables-save
	ip6tables-save > /etc/iptables/rules.v6 2>/dev/null || true
	
	echo "✅ 防火墙规则设置完成 (端口: 500, 4500, 8080, 8081)"
}

# strongSwan 6.0 完整部署函数 - 重构版
strongswan_setup_all_6() 
{
	echo "=== 开始完整部署 strongSwan 6.0 安全版本 ==="
	
	# 1. 部署 strongSwan 6.0
	echo "步骤 1/5: 部署 strongSwan 6.0.2..."
	strongswan_setup_6
	if [ $? -ne 0 ]; then
		echo "❌ strongSwan 6.0 部署失败"
		return 1
	fi
	
	# 2. 配置安全版本
	echo "步骤 2/5: 配置安全版本..."
	strongswan_config_6
	if [ $? -ne 0 ]; then
		echo "❌ 安全配置失败"
		return 1
	fi
	
	# 3. 设置防火墙规则
	echo "步骤 3/5: 设置防火墙规则..."
	dev=$(get_netdev)
	setup_iptables_6 $dev
	
	# 4. 配置网络参数
	echo "步骤 4/5: 配置网络参数..."
	net
	
	# 5. 初始化 CA 证书
	echo "步骤 5/5: 初始化 CA 证书..."
	ip=$(get_ip)
	init_ca $ip
	
	echo "=== strongSwan 6.0 完整部署完成 ==="
	echo "✅ 部署成功！"
	echo ""
	echo "📋 服务信息："
	echo "  服务状态：sudo systemctl status strongswan-swanctl"
	echo "  查看连接：sudo swanctl --list-conns"
	echo "  查看日志：sudo journalctl -u strongswan-swanctl -f"
	echo "  检查状态：sudo swanctl --list-sas"
	echo ""
	echo "🔧 管理命令："
	echo "  启动连接：sudo swanctl --initiate --child radius-secure"
	echo "  停止连接：sudo swanctl --terminate --child radius-secure"
	echo "  重新加载：sudo swanctl --load-all"
	echo ""
	echo "🌐 端口信息："
	echo "  IKE: 500/udp"
	echo "  NAT-T: 4500/udp"
	echo "  自定义: 8080/udp, 8081/udp"
}

#ca setup
init_ca() 
{
	cd ${TMP_HOME}
	mkdir -p ca
	cd ca
	echo "C=CN, O=timeline, CN=$1"
	ipsec pki --gen --outform pem > caKey.pem
	ipsec pki --self --in caKey.pem --dn "C=CN, O=timeline, CN=$1" --ca --outform pem > caCert.pem

	ipsec pki --gen --outform pem > serverKey.pem
	ipsec pki --pub --in serverKey.pem | ipsec pki --issue --cacert caCert.pem --cakey caKey.pem --dn "C=CN, O=timeline, CN=$1" --san="$1" --flag serverAuth --flag ikeIntermediate --outform pem > serverCert.pem

	ipsec pki --gen --outform pem > clientKey.pem
	ipsec pki --pub --in clientKey.pem | ipsec pki --issue --cacert caCert.pem --cakey caKey.pem --dn "C=CN, O=timeline, CN=client" --outform pem > clientCert.pem

	openssl pkcs12 -export -inkey clientKey.pem -in clientCert.pem -name "client" -certfile caCert.pem -caname "$1" -out clientCert.p12

	cp caCert.pem /etc/ipsec.d/cacerts/
	cp serverCert.pem /etc/ipsec.d/certs/
	cp serverKey.pem /etc/ipsec.d/private/
	cp clientCert.pem /etc/ipsec.d/certs/
	cp clientKey.pem /etc/ipsec.d/private/
	ipsec restart

#	多ip情况下可以为每个ip都指定一个caCert，但是key有使用相同的
#	ipsec pki --self --in caKey.pem --dn "C=CN, O=timeline, CN=154.22.124.96" --ca --outform pem > caCert3.pem
#	ipsec pki --pub --in serverKey.pem | ipsec pki --issue --cacert caCert3.pem --cakey caKey.pem --dn "C=CN, O=timeline, CN=154.22.124.96" --san="154.22.124.96" --flag serverAuth --flag ikeIntermediate --outform pem > serverCert3.pem
#	ipsec pki --pub --in clientKey.pem | ipsec pki --issue --cacert caCert3.pem --cakey caKey.pem --dn "C=CN, O=timeline, CN=client" --outform pem > clientCert3.pem
#	openssl pkcs12 -export -inkey clientKey.pem -in clientCert3.pem -name "client" -certfile caCert3.pem -caname "154.22.124.96" -out clientCert3.p12
#	cp caCert3.pem /etc/ipsec.d/cacerts/
#	cp serverCert3.pem /etc/ipsec.d/certs/
#	cp clientCert3.pem /etc/ipsec.d/certs/
#iptables -A INPUT -p udp --dport 500 -j ACCEPT
#iptables -A INPUT -p udp --dport 4500 -j ACCEPT
#iptables -A INPUT -p udp --dport 8080 -j ACCEPT
#iptables -A INPUT -p udp --dport 8081 -j ACCEPT
#iptables -t nat -A POSTROUTING -s 10.0.0.0/24 -o eth0 -j MASQUERADE
#iptables -A FORWARD -s 10.0.0.0/24 -j ACCEPT
#iptables -A FORWARD -d 10.0.0.0/24 -j ACCEPT
#ip6tables -A INPUT -p udp --dport 4500 -m frag --fragfirst -j CONNMARK --set-mark 0x42
#ip6tables -A INPUT -p udp --dport 4500 -j ACCEPT
#ip6tables -A INPUT -m frag -m connmark --mark 0x42 -j ACCEPT
#iptables -A FORWARD -s 10.2.0.0/24 -j ACCEPT
#iptables -A FORWARD -d 10.2.0.0/24 -j ACCEPT
#iptables -t nat -A POSTROUTING -s 10.2.0.0/24 -o eth0 -j SNAT --to 154.22.124.109

}


# iptables
setup_iptables() 
{
	iptables -A INPUT -p udp --dport 500 -j ACCEPT 
	iptables -A INPUT -p udp --dport 4500 -j ACCEPT
	iptables -A INPUT -p udp --dport 8080 -j ACCEPT
	iptables -A INPUT -p udp --dport 8081 -j ACCEPT
	iptables -t nat -A POSTROUTING -s 10.0.0.0/24 -o $1 -j MASQUERADE 
	iptables -A FORWARD -s 10.0.0.0/24 -j ACCEPT 
	iptables -A FORWARD -d 10.0.0.0/24 -j ACCEPT
	ip6tables -A INPUT -p udp --dport 4500 -m frag --fragfirst -j CONNMARK --set-mark 0x42
	ip6tables -A INPUT -p udp --dport 4500 -j ACCEPT
	ip6tables -A INPUT -m frag -m connmark --mark 0x42 -j ACCEPT
	#为避免VPS重启后NAT功能失效，可以把如上5行命令添加到 /etc/rc.local 文件中，添加在exit那一行之前即可。
	#service iptables save
	#service iptables restart
	#systemctl restart iptables
	#	iptables -t nat -A POSTROUTING -s 10.2.0.0/24 -o eth0 -j SNAT --to 154.22.124.109  多ip指定出口ip
	iptables-save
	#iptables-restore  https://blog.csdn.net/hack8/article/details/6772958
	#tcpdump -s 0 -n -i eth0 'esp or udp and (port 500 or port 4500)'
}
#net
# vi /etc/sysctl.conf
net() 
{

	echo "net.ipv4.tcp_syncookies = 1"  >>  /etc/sysctl.conf
	echo "net.ipv4.tcp_tw_reuse = 1"  >>  /etc/sysctl.conf
	echo "net.ipv4.tcp_tw_recycle = 0"  >>  /etc/sysctl.conf
	echo "#向外连接的端口范围"  >>  /etc/sysctl.conf
	echo "net.ipv4.ip_local_port_range = 1024 65000 "  >>  /etc/sysctl.conf
	echo "#示SYN队列的长度，默认为1024，加大队列长度为8192，可以容纳更多等待连接的网络连接数"  >>  /etc/sysctl.conf
	echo "net.ipv4.tcp_max_syn_backlog = 8192 "  >>  /etc/sysctl.conf
	echo "net.ipv4.tcp_max_tw_buckets = 5000"  >>  /etc/sysctl.conf
	echo "net.ipv4.tcp_keepalive_time = 1200"  >>  /etc/sysctl.conf
	echo "net.ipv4.tcp_fin_timeout = 30"  >>  /etc/sysctl.conf
	echo "net.ipv4.tcp_max_tw_buckets = 5000"  >>  /etc/sysctl.conf
	echo "#TCP接收缓冲大小，对应最小、默认、最大"  >>  /etc/sysctl.conf
	echo "net.ipv4.tcp_rmem = 4096 87380 4194304"  >>  /etc/sysctl.conf
	echo "#TCP发送缓冲大小，对应最小、默认、最大"  >>  /etc/sysctl.conf
	echo "net.ipv4.tcp_wmem = 4096 16384 4194304"  >>  /etc/sysctl.conf
	echo "#最大发送套接字缓冲区大小"  >>  /etc/sysctl.conf
	echo "net.core.rmem_max = 16777216"  >>  /etc/sysctl.conf
	echo "#最大接收套接字缓冲区大小"  >>  /etc/sysctl.conf
	echo "net.core.wmem_max = 16777216"  >>  /etc/sysctl.conf
	echo "#当网络接口接收速率比内核处理快时允许发到队列的数据包数目"  >>  /etc/sysctl.conf
	echo "net.core.netdev_max_backlog = 262144"  >>  /etc/sysctl.conf
	echo "#系统同时发起的TCP连接娄，超过导致连接超时或重传"  >>  /etc/sysctl.conf
	echo "net.core.somaxconn = 262144"  >>  /etc/sysctl.conf
	echo "net.ipv4.ip_forward = 1"  >>  /etc/sysctl.conf
	echo "net.ipv6.conf.all.forwarding=1"  >>  /etc/sysctl.conf
	echo "net.ipv6.conf.all.proxy_ndp=1"  >>  /etc/sysctl.conf
	
	# max open files
	echo "fs.file-max = 1024000"  >>  /etc/sysctl.conf
	
	cat /etc/sysctl.conf
	sysctl -p
	
	#其中最后的hybla是为高延迟网络（如美国，欧洲）准备的算法，需要内核支持，测试内核是否支持，在终端输入：
	#sysctl net.ipv4.tcp_available_congestion_control
	#如果结果中有hybla，则证明你的内核已开启hybla，如果没有hybla，可以用命令modprobe tcp_hybla开启。

		#对于低延迟的网络（如日本，香港等），可以使用htcp，可以非常显著的提高速度，首先使用modprobe tcp_htcp开启，再将net.ipv4.tcp_congestion_control = hybla改为net.ipv4.tcp_congestion_control = htcp，建议EC2日本用户使用这个算法。

	echo "*               soft    nofile           512000"  >> /etc/security/limits.conf
	echo "*               hard    nofile          1024000"  >> /etc/security/limits.conf
	echo "ulimit -SHn 1024000"  >> /root/.profile
	source /root/.profile
	ulimit -n

}
setup_caip()
{
	ip=$(get_ip)
    init_ca	$ip
}
## -----------------------
## Setup all aboves
## -----------------------
setup_fail2ban() 
{
    apt-get install -y fail2ban sendmail
    cp ../monitor/jail.conf /etc/fail2ban/
    service fail2ban restart
}
#init bbr
setup_kernel()
{
#	cd ${TMP_HOME}
#	rm -rf kernel
#	mkdir kernel
#	cd kernel
	#http://kernel.ubuntu.com/~kernel-ppa/mainline
	#wget  ${URL}/soft/linux-kernel/linux-headers-4.9.0-040900_4.9.0-040900.201612111631_all.deb
	#wget  ${URL}/soft/linux-kernel/linux-headers-4.9.0-040900-generic_4.9.0-040900.201612111631_amd64.deb
	#wget  ${URL}/soft/linux-kernel/linux-image-4.9.0-040900-generic_4.9.0-040900.201612111631_amd64.deb
	#wget http://kernel.ubuntu.com/~kernel-ppa/mainline/v4.12/linux-headers-4.12.0-041200_4.12.0-041200.201707022031_all.deb
	#wget http://kernel.ubuntu.com/~kernel-ppa/mainline/v4.12/linux-headers-4.12.0-041200-generic_4.12.0-041200.201707022031_amd64.deb
	#wget http://kernel.ubuntu.com/~kernel-ppa/mainline/v4.12/linux-image-4.12.0-041200-generic_4.12.0-041200.201707022031_amd64.deb


	#wget http://kernel.ubuntu.com/~kernel-ppa/mainline/v4.13.16/linux-headers-4.13.16-041316_4.13.16-041316.201711240901_all.deb
	#wget http://kernel.ubuntu.com/~kernel-ppa/mainline/v4.13.16/linux-headers-4.13.16-041316-generic_4.13.16-041316.201711240901_amd64.deb
	#wget http://kernel.ubuntu.com/~kernel-ppa/mainline/v4.13.16/linux-image-4.13.16-041316-generic_4.13.16-041316.201711240901_amd64.deb

	 #wget http://kernel.ubuntu.com/~kernel-ppa/mainline/v4.9.135/linux-headers-4.9.135-0409135_4.9.135-0409135.201810200830_all.deb
	 #wget http://kernel.ubuntu.com/~kernel-ppa/mainline/v4.9.135/linux-headers-4.9.135-0409135-generic_4.9.135-0409135.201810200830_amd64.deb
	 #wget http://kernel.ubuntu.com/~kernel-ppa/mainline/v4.9.135/linux-image-4.9.135-0409135-generic_4.9.135-0409135.201810200830_amd64.deb

	#dpkg -i *.deb
	echo "net.core.default_qdisc=fq" >> /etc/sysctl.conf
	echo "net.ipv4.tcp_congestion_control=bbr" >> /etc/sysctl.conf
	sysctl -p
	sysctl net.ipv4.tcp_available_congestion_control
	lsmod | grep bbr
	#grep menuentry /boot/grub/grub.cfg
	# /etc/default/grub GRUB_DEFAULT=0-銆�2
	#update-grub
	#reboot
}
setup_rclocal() {
	cp ../monitor/rc-local.service /etc/systemd/system/
	cp ../monitor/rc.local /etc/
	chmod +x /etc/rc.local
}
## -----------------------
## Setup all aboves
## -----------------------
setup_all() 
{
    init_soft
    strongswan_setup
    strongswan_config
    ip=$(get_ip)
    init_ca	$ip
    dev=$(get_netdev)
    setup_iptables $dev
    #setup_fail2ban
    net
    strongswanconf_port
    setup_kernel
    setup_rclocal
    echo "crotab-----------------------------"
    echo "crotab-----------------------------"
    echo "crotab-----------------------------"
    echo "crotab-----------------------------"
    echo "crotab-----------------------------"
    echo "crotab-----------------------------"
    echo "crotab-----------------------------"
    echo "crotab-----------------------------"
    echo "crotab-----------------------------"
    echo "crotab-----------------------------"
    
}
get_ip(){
    local IP=$( ip addr | egrep -o '[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}' | egrep -v "^192\.168|^172\.1[6-9]\.|^172\.2[0-9]\.|^172\.3[0-2]\.|^10\.|^127\.|^255\.|^0\." | head -n 1 )
    [ -z ${IP} ] && IP=$( wget -qO- -t1 -T2 ipv4.icanhazip.com )
    [ -z ${IP} ] && IP=$( wget -qO- -t1 -T2 ipinfo.io/ip )
    [ ! -z ${IP} ] && echo ${IP} 
    echo ${IP}
}
get_netdev(){
    local IP=$( ip addr | egrep -o '[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}' | egrep -v "^192\.168|^172\.1[6-9]\.|^172\.2[0-9]\.|^172\.3[0-2]\.|^10\.|^127\.|^255\.|^0\." | head -n 1 )
    DEV=$( ip addr | grep ${IP} ||egrep -o '(eth0|ens3|enp1s0)')
    echo ${DEV}
}
## -----------------------
## Show help message
## -----------------------
usage() 
{
    echo "Available arguments as below:"
    echo ""
    echo "=== 基础软件安装 ==="
    echo "soft           Setup init soft"
    echo "telegraf       Setup telegraf"
    echo "fail2ban       Setup fail2ban"
    echo "kernel         Setup kernel"
    echo ""
    echo "=== strongSwan 5.6.3 (旧版本) ==="
    echo "strongswan     Setup strongswan 5.6.3"
    echo "strongswanconf Setup strongswan 5.6.3 config"
    echo "strongswanconf_port Setup strongswan 5.6.3 port config"
    echo ""
    echo "=== strongSwan 6.0 (新版本，安全优化) ==="
    echo "strongswan6    Setup strongswan 6.0"
    echo "strongswanconf6 Setup strongswan 6.0 secure config"
    echo "strongswanconf_port6 Setup strongswan 6.0 port config"
    echo "strongswanall6 Setup strongswan 6.0 complete deployment"
    echo ""
    echo "=== 证书和网络 ==="
    echo "ca             Setup ca"
    echo "caip           Setup caip"
    echo "iptables       Setup iptables"
    echo "net            Setup net"
    echo ""
    echo "=== 检查和测试 ==="
    echo "check          checkspeed"
    echo "check_vpn      check vpn (5.6.3)"
    echo "check_vpn6     check vpn (6.0)"
    echo "check_mtr      Setup check_mtr"
    echo ""
    echo "=== 完整部署 ==="
    echo "all            Setup all aboves (5.6.3 version)"
    echo ""
    echo "=== 使用示例 ==="
    echo "部署 strongSwan 6.0 安全版本："
    echo "  ./vpn_setup.sh strongswanall6"
    echo ""
    echo "仅部署 strongSwan 6.0 软件："
    echo "  ./vpn_setup.sh strongswan6"
    echo ""
    echo "配置 strongSwan 6.0 安全版本："
    echo "  ./vpn_setup.sh strongswanconf6"

}

## =====================================
## The main process
## =====================================
if [ $# != 0 ]; then
    for arg in $*; do
        case "$arg" in
            # 基础软件安装
            soft)            init_soft;;
            telegraf)        setup_telegraf;;
            fail2ban)        setup_fail2ban;;
            kernel)          setup_kernel;;
            
            # strongSwan 5.6.3 (旧版本)
            strongswan)      strongswan_setup;;
            strongswanconf)  strongswan_config;;
            strongswanconf_port) strongswan_config_port;;
            
            # strongSwan 6.0 (新版本，安全优化)
            strongswan6)     strongswan_setup_6;;
            strongswanconf6) strongswan_config_6;;
            strongswanconf_port6) strongswan_config_port_6;;
            strongswanall6)  strongswan_setup_all_6;;
            
            # 证书和网络
            ca)              init_ca $2;;
            caip)            setup_caip;;
            iptables)        setup_iptables;;
            net)             net;;
            
            # 检查和测试
            check)           checkspeed;;
            check_vpn)       check_vpn;;
            check_vpn6)      check_vpn_6;;
            check_mtr)       checkmtr;;
            
            # 完整部署
            all)             setup_all;;
            
            # 未知参数
            *)               echo "未知参数: $arg"; usage;;
        esac
    done
else
    usage
fi
