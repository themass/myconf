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
  sudo apt-get install -y build-essential libssl-dev libgmp-dev libcurl4-openssl-dev pkg-config autotools-dev libtool autoconf automake libsystemd-dev libiptc-dev libip4tc-dev libip6tc-dev

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
	sudo systemctl start strongswan
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

# strongSwan 6.0.2 部署函数 - 简单版本
strongswan_setup_6() {
	echo "=== 部署 strongSwan 6.0.2 ==="
	cd ${TMP_HOME}
	
	# 安装依赖 - Ubuntu 18.04 完整版本
	sudo apt-get update
	sudo apt-get install -y \
		build-essential \
		libssl-dev \
		libgmp-dev \
		libcurl4-openssl-dev \
		pkg-config \
		autotools-dev \
		libtool \
		autoconf \
		automake \
		libsystemd-dev \
		libiptc-dev \
		libip4tc-dev \
		libip6tc-dev \
		libpam0g-dev \
		libmysqlclient-dev \
		libsqlite3-dev \
		libldap2-dev \
		libsoup2.4-dev \
		libunbound-dev \
		libcharon-extra-plugins \
		libstrongswan-extra-plugins \
		libstrongswan-standard-plugins \
		strongswan-dev

	# 下载源码
	if [ ! -d "strongswan-6.0.2" ]; then
		wget https://download.strongswan.org/strongswan-6.0.2.tar.bz2 --no-check-certificate
		tar -jxvf strongswan-6.0.2.tar.bz2
	fi
	cd strongswan-6.0.2
	# 配置编译
	./configure --prefix=/usr --sysconfdir=/etc --enable-openssl --enable-eap-radius --enable-eap-identity --enable-eap-md5 --enable-eap-mschapv2 --enable-eap-tls --enable-eap-ttls --enable-vici --enable-swanctl --enable-systemd --enable-kernel-netlink --enable-kernel-libipsec
		# 编译安装
	make -j$(nproc) && sudo make install
	
	# 创建用户
	sudo groupadd -r strongswan 2>/dev/null || true
	sudo useradd -r -g strongswan -s /bin/false -d /var/lib/strongswan strongswan 2>/dev/null || true
	
	# 创建目录
	sudo mkdir -p /etc/swanctl/{private,x509,scripts} /var/log/strongswan /var/lib/strongswan
	sudo chown -R strongswan:strongswan /etc/swanctl /var/log/strongswan /var/lib/strongswan

	# 创建服务文件
	cd ${WORKDIR}/myconf/shell
	cp ../strongswan_6.0_conf/strongswan.service /etc/systemd/system/strongswan.service

# 创建必要的目录
  echo "创建必要的目录..."
  sudo mkdir -p /var/log/strongswan
  sudo mkdir -p /etc/swanctl/{private,x509,scripts}
  sudo mkdir -p /var/run/charon

  # 设置权限
  echo "设置权限..."
  sudo chown -R strongswan:strongswan /var/log/strongswan /etc/swanctl /var/run/charon 2>/dev/null || true
  sudo chmod 755 /var/log/strongswan /etc/swanctl /var/run/charon
  sudo chmod 700 /etc/swanctl/private 2>/dev/null || true

  sudo ln -sf /usr/lib/ipsec/libstrongswan.so.0 /usr/lib/libstrongswan.so.0
  sudo ln -sf /usr/lib/ipsec/libcharon.so.0 /usr/lib/libcharon.so.0
  # 更新库缓存
  sudo ldconfig

	# 启动服务
	sudo systemctl daemon-reload
	sudo systemctl enable strongswan
	sudo systemctl start strongswan &
	sleep 2
	echo "✅ strongSwan 6.0.2 部署完成"
}

# strongSwan 6.0.2 配置函数 (默认端口)
strongswan_config_6() {
	echo "=== 开始配置 strongSwan 6.0.2 (包含所有端口) ==="
	cd ${WORKDIR}/myconf/shell

	# 获取服务器IP
	SERVER_IP=$(get_ip)
	if [ -z "$SERVER_IP" ]; then
		echo "❌ 无法获取服务器IP地址"
		return 1
	fi
	echo "服务器IP: $SERVER_IP"

	# 复制配置文件
	echo "复制配置文件..."
	mv /etc/strongswan.conf /etc/strongswan.conf.bak
	mv /etc/swanctl/swanctl.conf /etc/swanctl/swanctl.conf.bak
	sudo cp ../strongswan_6.0_conf/strongswan.conf /etc/strongswan.conf
	sudo cp ../strongswan_6.0_conf/swanctl.conf /etc/swanctl/swanctl.conf
	sudo cp ../strongswan_6.0_conf/swanctl.conf /etc/swanctl.conf
	
	# 替换服务器IP
	echo "替换服务器IP..."
	sudo sed -i "s/{{SERVER_IP}}/$SERVER_IP/g" /etc/swanctl/swanctl.conf
	sudo sed -i "s/{{SERVER_IP}}/$SERVER_IP/g" /etc/swanctl.conf



	echo "注意：证书文件需要单独运行 caip6 生成"
	# 重启服务应用配置
	echo "重启服务应用配置..."
	sudo systemctl daemon-reload
	sudo systemctl restart strongswan &
	sleep 3
	# 加载配置
	echo "加载配置..."
	sudo swanctl --load-all
	sleep 2
	# 验证配置
	echo "验证配置..."
	sudo swanctl --list-conns
	netstat -ulpn

	# 检查服务状态
	echo "检查服务状态..."
	if ! sudo systemctl is-active --quiet strongswan; then
		echo "❌ 服务启动失败，请检查配置"
		echo "服务日志："
		sudo systemctl status strongswan --no-pager -l
		sudo journalctl -u strongswan --no-pager -n 40
		return 1
	fi
	echo "✅ strongSwan 6.0.2 配置完成！"
	echo "检查配置：sudo swanctl --list-conns"
	echo "查看日志：sudo journalctl -u strongswan-swanctl -f"
	echo "=== 配置完成 ==="
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

# strongSwan 6.0.2 证书生成函数
caip6() {
	echo "=== 开始生成 strongSwan 6.0.2 证书 ==="
	cd ${TMP_HOME}
	mkdir -p ca6
	cd ca6

	# 获取服务器外网IP（用于证书生成）
	SERVER_IP=$(get_ip)
	if [ -z "$SERVER_IP" ]; then
		echo "❌ 无法获取服务器外网IP地址"
		return 1
	fi
	echo "服务器外网IP: $SERVER_IP"

	# 确保 strongswan.conf 存在
	if [ ! -f "/etc/strongswan.conf" ]; then
		echo "创建基础 strongswan.conf..."
		sudo mkdir -p /etc/swanctl/{x509,private}
		sudo cp ${WORKDIR}/myconf/strongswan_6.0_conf/strongswan.conf /etc/strongswan.conf
	fi

	# 生成 CA 证书
	echo "生成 CA 证书..."
	pki --gen --outform pem > caKey.pem
	pki --self --in caKey.pem --dn "C=CN, O=timeline, CN=$SERVER_IP" --ca --outform pem > caCert.pem

	# 生成服务器证书
	echo "生成服务器证书..."
	pki --gen --outform pem > serverKey.pem
	pki --pub --in serverKey.pem | pki --issue --cacert caCert.pem --cakey caKey.pem --dn "C=CN, O=timeline, CN=$SERVER_IP" --san="$SERVER_IP" --flag serverAuth --flag ikeIntermediate --outform pem > serverCert.pem

	# 生成客户端证书
	echo "生成客户端证书..."
	pki --gen --outform pem > clientKey.pem
	pki --pub --in clientKey.pem | pki --issue --cacert caCert.pem --cakey caKey.pem --dn "C=CN, O=timeline, CN=client" --outform pem > clientCert.pem

	# 生成 PKCS12 格式客户端证书
	echo "生成 PKCS12 客户端证书..."
	openssl pkcs12 -export -inkey clientKey.pem -in clientCert.pem -name "client" -certfile caCert.pem -caname "$SERVER_IP" -out clientCert.p12 -passout pass:

	# 注意：证书和端口无关，只需要一套证书即可

	# 复制到 strongSwan 6.0.2 目录
	echo "复制证书到 strongSwan 6.0.2 目录..."
	sudo mkdir -p /etc/swanctl/{x509,private,x509ca}

	# 复制基础证书到 x509 目录
	sudo cp caCert.pem /etc/swanctl/x509/
	sudo cp serverCert.pem /etc/swanctl/x509/
	sudo cp serverKey.pem /etc/swanctl/private/
	sudo cp clientCert.pem /etc/swanctl/x509/
	sudo cp clientKey.pem /etc/swanctl/private/
	sudo cp clientCert.p12 /etc/swanctl/x509/

	# 复制 CA 证书到 x509ca 目录（strongSwan 6.0.2 期望的位置）
	sudo cp caCert.pem /etc/swanctl/x509ca/

	# 注意：端口配置不需要额外的证书，使用同一套证书即可

	# 设置权限
	echo "设置证书权限..."
	sudo chown -R strongswan:strongswan /etc/swanctl
	sudo chmod 644 /etc/swanctl/x509/*.pem
	sudo chmod 600 /etc/swanctl/private/*.pem
	sudo chmod 644 /etc/swanctl/x509/*.p12
	sudo chmod 644 /etc/swanctl/x509ca/*.pem

	# 重启服务以应用证书
	echo "重启服务应用证书..."
	sudo systemctl restart strongswan &
	sleep 3
	# 加载配置
	echo "加载配置..."
	sudo swanctl --load-all
	sleep 2
	# 验证证书
	echo "验证证书..."
	sudo swanctl --list-certs

	echo "✅ strongSwan 6.0.2 证书生成完成！"
	echo "证书位置：/etc/swanctl/x509/ 和 /etc/swanctl/private/"
	echo "查看证书：sudo swanctl --list-certs"
	echo "=== 证书生成完成 ==="
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
    echo ${IP}
}
get_internal_ip(){
    local IP=$( ip addr | egrep -o '[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}' | egrep "^192\.168|^172\.1[6-9]\.|^172\.2[0-9]\.|^172\.3[0-2]\.|^10\." | head -n 1 )
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
    echo "=== strongSwan 6.0.2 (新版本，安全优化) ==="
    echo "strongswan6    Setup strongswan 6.0.2"
    echo "strongswanconf6 Setup strongswan 6.0.2 config (一键完成所有配置)"
    echo ""
    echo ""
    echo "=== 证书和网络 ==="
    echo "ca             Setup ca"
    echo "caip           Setup caip (5.6.3)"
    echo "caip6          Setup caip6 (6.0.2)"
    echo "iptables       Setup iptables"
    echo "net            Setup net"
    echo ""
    echo "=== 检查和测试 ==="
    echo "check          checkspeed"
    echo "check_vpn      check vpn (5.6.3)"
    echo "check_mtr      Setup check_mtr"
    echo ""
    echo "=== 完整部署 ==="
    echo "all            Setup all aboves (5.6.3 version)"
    echo ""
    echo "=== 使用示例 ==="
    echo "部署 strongSwan 6.0.2 配置 (默认端口):"
    echo "  bash vpn_setup.sh strongswan6"
    echo "  bash vpn_setup.sh strongswanconf6"
    echo "  bash vpn_setup.sh caip6"
    echo ""
    echo ""
    echo "部署 strongSwan 5.6.3 默认配置："
    echo "  bash vpn_setup.sh strongswan"
    echo "  bash vpn_setup.sh strongswanconf"
    echo "  bash vpn_setup.sh caip"
    echo ""
    echo "部署 strongSwan 5.6.3 端口配置："
    echo "  bash vpn_setup.sh strongswan"
    echo "  bash vpn_setup.sh strongswanconf_port"
    echo "  bash vpn_setup.sh caip"

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

            # strongSwan 6.0.2 (新版本，安全优化)
            strongswan6)     strongswan_setup_6;;
            strongswanconf6) strongswan_config_6;;
            
            
            # 证书和网络
            ca)              init_ca $2;;
            get_ip)              get_ip ;;
            caip)            setup_caip;;
            caip6)           caip6;;
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
