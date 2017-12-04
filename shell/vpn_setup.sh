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
	apt-get update
	apt-get install sysstat vim build-essential lrzsz  tree dstat git dos2unix unzip libtalloc2   libtalloc-dev libxml2-dev php-pear aptitude	#编译环境
	aptitude install libgmp10 libgmp3-dev libssl-dev pkg-config libpcsclite-dev libpam0g-dev   curl  #编译所需要的软件
}
strongswan_setup() 
{
	cd ${TMP_HOME}
	wget http://download.strongswan.org/strongswan-5.6.0.tar.bz2
	tar -jxvf strongswan-5.6.0.tar.bz2 && cd strongswan-5.6.0
	./configure --prefix=/usr --sysconfdir=/etc  --enable-openssl --enable-nat-transport --disable-mysql --disable-ldap  --disable-static --enable-shared --enable-md4 --enable-eap-mschapv2 --enable-eap-aka --enable-eap-aka-3gpp2  --enable-eap-gtc --enable-eap-identity --enable-eap-md5 --enable-eap-peap --enable-eap-radius --enable-eap-sim --enable-eap-sim-file --enable-eap-simaka-pseudonym --enable-eap-simaka-reauth --enable-eap-simaka-sql --enable-eap-tls --enable-eap-tnc --enable-eap-ttls
	make && make install
	ipsec start 
	cd ..
}
strongswan_config() 
{
	#unzip strongswan_conf.zip
	#dos2unix strongswan_conf/ipsec.conf
	#dos2unix strongswan_conf/charon.conf
	#dos2unix strongswan_conf/ipsec.secrets
	#
	#cp  /etc/ipsec.conf /etc/ipsec.conf.bak
	#cp  strongswan_conf/ipsec.conf /etc/ipsec.conf
    #
	#cp  /etc/strongswan.d/charon.conf /etc/strongswan.d/charon.conf.bak
	#cp  strongswan_conf/charon.conf /etc/strongswan.d/charon.conf
    #
	#cp  /etc/ipsec.secrets  /etc/ipsec.secrets.bak
	#cp  strongswan_conf/ipsec.secrets /etc/ipsec.secrets
	
	
	cp  /etc/ipsec.conf /etc/ipsec.conf.bak
	cp  ../strongswan_conf/ipsec.conf /etc/ipsec.conf
    
	cp  /etc/strongswan.d/charon.conf /etc/strongswan.d/charon.conf.bak
	cp  ../strongswan_conf/charon.conf /etc/strongswan.d/charon.conf
    
	cp  /etc/ipsec.secrets  /etc/ipsec.secrets.bak
	cp  ../strongswan_conf/ipsec.secrets /etc/ipsec.secrets
	
	cp  ../strongswan_conf/strongswan.conf /etc/strongswan.conf
	
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
}


# iptables
setup_iptables() 
{
	iptables -A INPUT -p udp --dport 500 -j ACCEPT 
	iptables -A INPUT -p udp --dport 4500 -j ACCEPT 
	iptables -t nat -A POSTROUTING -s 10.0.0.0/24 -o ens3 -j MASQUERADE 
	iptables -A FORWARD -s 10.0.0.0/24 -j ACCEPT 
	iptables -A FORWARD -d 10.0.0.0/24 -j ACCEPT
	ip6tables -A INPUT -p udp --dport 4500 -m frag --fragfirst -j CONNMARK --set-mark 0x42
	ip6tables -A INPUT -p udp --dport 4500 -j ACCEPT
	ip6tables -A INPUT -m frag -m connmark --mark 0x42 -j ACCEPT
	#为避免VPS重启后NAT功能失效，可以把如上5行命令添加到 /etc/rc.local 文件中，添加在exit那一行之前即可。
	#service iptables save
	#service iptables restart
	#systemctl restart iptables
	iptables-save
	#iptables-restore
	#tcpdump -s 0 -n -i eth0 'esp or udp and (port 500 or port 4500)'
}
#net
# vi /etc/sysctl.conf
net() 
{

	echo "net.ipv4.tcp_syncookies = 1"  >>  /etc/sysctl.conf
	echo "net.ipv4.tcp_tw_reuse = 0"  >>  /etc/sysctl.conf
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
	cat /etc/sysctl.conf
	sysctl -p
}
## -----------------------
## Setup all aboves
## -----------------------
setup_fail2ban() 
{
    apt-get install fail2ban
    cp ../monitor/jail.conf /etc/fail2ban/
    service fail2ban restart
}
## -----------------------
## Setup all aboves
## -----------------------
setup_all() 
{
    init_soft
    strongswan_setup
    strongswan_config
    init_ca	
    setup_iptables   
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
    echo "iptables         Setup iptables"
    echo "net    Setup net"
    echo "fail2ban    Setup fail2ban"
    echo "all           Setup all aboves"
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
	    iptables)          setup_iptables;;
	    strongswanconf)          strongswan_config;;
	    net)          net;;
	     fail2ban)          setup_fail2ban;;
	    all)          setup_all;;
        esac
    done
else
    usage
fi
