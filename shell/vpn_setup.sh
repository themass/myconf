#init soft

#http://it.zhaozhao.info/archives/41127
#https://segmentfault.com/a/1190000002540601
#http://www.cnblogs.com/hyzhou/category/336618.html
WORKDIR=/root/work
TMP_HOME=/root/soft
PWD=`pwd`
ip=`/sbin/ifconfig -a|grep inet|grep -v 127.0.0.1|grep -v inet6|grep -v 10. |awk '{print $2}'|tr -d "addr:"`
init_soft() 
{
	apt-get update
	apt-get install build-essential lrzsz  tree dstat git dos2unix unzip libtalloc2   libtalloc-dev libxml2-dev php-pear	#编译环境
	aptitude install libgmp10 libgmp3-dev libssl-dev pkg-config libpcsclite-dev libpam0g-dev     #编译所需要的软件
}
strongswan_setup() 
{
	cd ${TMP_HOME}
	wget http://download.strongswan.org/strongswan-5.2.2.tar.bz2
	tar -jxvf strongswan-5.2.2.tar.bz2 && cd strongswan-5.2.2
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
	echo "C=CN, O=timeline, CN=${ip}"
	ipsec pki --gen --outform pem > caKey.pem
	ipsec pki --self --in caKey.pem --dn "C=CN, O=timeline, CN=${ip}" --ca --outform pem > caCert.pem

	ipsec pki --gen --outform pem > serverKey.pem
	ipsec pki --pub --in serverKey.pem | ipsec pki --issue --cacert caCert.pem --cakey caKey.pem --dn "C=CN, O=timeline, CN=${ip}" --san="${ip}" --flag serverAuth --flag ikeIntermediate --outform pem > serverCert.pem

	ipsec pki --gen --outform pem > clientKey.pem
	ipsec pki --pub --in clientKey.pem | ipsec pki --issue --cacert caCert.pem --cakey caKey.pem --dn "C=CN, O=timeline, CN=client" --outform pem > clientCert.pem

	openssl pkcs12 -export -inkey clientKey.pem -in clientCert.pem -name "client" -certfile caCert.pem -caname "${ip}" -out clientCert.p12

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
	iptables -t nat -A POSTROUTING -s 10.0.0.0/24 -o eth1 -j MASQUERADE 
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
}
#net
# vi /etc/sysctl.conf
net() 
{
	net.ipv4.ip_forward = 1
	net.ipv6.conf.all.forwarding=1
	sysctl -p
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
	    ca)          init_ca;;
	    iptables)          setup_iptables;;
	    strongswanconf)          strongswan_config;;
	    net)          net;;
	    all)          setup_all;;
        esac
    done
else
    usage
fi
