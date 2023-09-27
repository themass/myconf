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
    echo "soft           Setup init soft"
    echo "strongswan          Setup strongswan"
    echo "strongswanconf          Setup strongswan config"
    echo "ca           Setup ca"
    echo "caip           Setup caip"
    echo "iptables         Setup iptables"
    echo "net    Setup net"
    echo "fail2ban    Setup fail2ban"
    echo "check    checkspeed"
     echo "check_vpn    check vpn"
     echo "net    Setup net"
      echo "strongswanconf_port    Setup strongswanconf_port"
    echo "all           Setup all aboves"
    echo "telegraf          Setup telegraf"
    echo "check_mtr          Setup check_mtr"
    echo "kernel          Setup kernel"

}

## =====================================
## The main process
## =====================================
if [ $# != 0 ]; then
    for arg in $*; do
        case "$arg" in
            soft)            init_soft;;
            strongswan)          strongswan_setup;;
	      ca)          init_ca $2;;
	     caip)          setup_caip;;
	    iptables)          setup_iptables;;
	    strongswanconf)          strongswan_config;;
	    strongswanconf_port)          strongswan_config_port;;
	    net)          net;;
	     fail2ban)          setup_fail2ban;;
	    check)          checkspeed;;
	    check_vpn)          check_vpn;;
	    telegraf)         setup_telegraf;;
	    check_mtr)         checkmtr;;
	   kernel)         setup_kernel;;
	    all)          setup_all;;
        esac
    done
else
    usage
fi
