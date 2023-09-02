#!/bin/bash
## -----------------------
## Version setting
## -----------------------

#URL=http://10.117.233.81:9003
URL=http://file.sspacee.com


APP_HOME=/root/local
TMP_HOME=/root/soft

MYSQL_VERSION=mysql-5.6.40-linux-glibc2.12-x86_64
RADIUS_VERSION=freeradius-server

mkdir -p ${APP_HOME}
mkdir -p ${TMP_HOME}
PWD=`pwd`
setup_check()
{
	ps -aux| grep mysql
	ps -aux| grep nginx
	ps -aux| grep ips
	ps -aux| grep radiu
	iptables --list
	ps -aux| grep php
	ps -aux| grep tomcat
	ps -aux| grep redis
}
setup_kernel()
{
	cd ${TMP_HOME}
	rm -rf kernel
	mkdir kernel
	cd kernel
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

## -----------------------
## Setup MySQL
## -----------------------
setup_mysql() {
    #https://cdn.mysql.com//Downloads/MySQL-5.6/mysql-5.6.40-linux-glibc2.12-x86_64.tar.gz
	  shelldir=`pwd`
    useradd -r -m -s /bin/bash mysql
    apt install libaio1
    apt install libnuma1
    cd /root/soft
    rm -rf /home/mysql/db_data/*
    wget https://cdn.mysql.com/archives/mysql-5.6/mysql-5.6.40-linux-glibc2.12-x86_64.tar.gz --no-check-certificate
    cd /root/local
    tar -zxvf /root/soft/mysql-5.6.40-linux-glibc2.12-x86_64.tar.gz
    mv mysql-5.6.40-linux-glibc2.12-x86_64 mysql-5.6.40
    rm -rf /home/mysql/mysql
    ln -s /root/local/mysql-5.6.40 /home/mysql/mysql
    rm -rf /usr/local/mysql
    ln -s /root/local/mysql-5.6.40 /usr/local/mysql
    cd /home/mysql/mysql
    chown -R mysql .
    chgrp -R mysql .
    mkdir -p /home/mysql/db_data
    chown mysql:mysql /home/mysql/db_data
    mkdir -p /home/mysql/log_data
    chown mysql:mysql /home/mysql/log_data
    rm -rf /var/log/mysql  /var/run/mysqld /var/lib/mysql
    mkdir -p /var/log/mysql
    mkdir -p /var/run/mysqld
    mkdir -p /var/lib/mysql
    mkdir -p /usr/share/mysql
    chown mysql:mysql /var/log/mysql
    chown mysql:mysql /var/run/mysqld
    chown mysql:mysql /var/lib/mysql
    scripts/mysql_install_db --user=mysql --basedir=. --datadir=/home/mysql/db_data
    chown -R root .
    chown -R mysql data
    echo ${shelldir}
    cd ${shelldir}
    rm -f /etc/my.cnf
    cp ../mysql/my.cnf /etc/my.cnf
    rm /etc/mysql/my.cnf
    echo 'export PATH=$PATH:/usr/local/mysql/bin'
    cp /home/mysql/mysql/share/english/errmsg.sys  /usr/share/mysql/
    mysqld_safe  &
    #show variables like "%char%"; ->utf-8

#    mysql -u root -p
#    use mysql;
#    UPDATE user SET password=password('Themass@5296') WHERE user='root'
#    CREATE USER 'radius'@'%' IDENTIFIED BY 'Themass@5296'
#    CREATE USER 'vpn@server'@'%' IDENTIFIED BY 'Themass@5296'
#    CREATE USER 'root'@'%' IDENTIFIED BY 'Themass@5296'
#    flush privileges
}
#/////
#
setup_radius() {
    shelldir=`pwd`
    cd /root/soft
    apt-get install  freeradius-mysql
    rm -rf /usr/local/etc/raddb

    git clone https://github.com/openssl/openssl
    cd openssl/
    git checkout OpenSSL_1_0_1-stable
    ./configure
    make

    wget https://github.com/FreeRADIUS/freeradius-server/archive/refs/tags/release_2_1_12.tar.gz
    tar -zxvf release_2_1_12.tar.gz
    cd freeradius-server-release_2_1_12/
    ./configure --with-openssl-includes=/root/soft/openssl/ --with-openssl-libraries=/root/soft/openssl/
    make
    make install

    echo  ' test  radiusd -X'
	  echo 'radtest vpn themass localhost 1812 testing123'
	  echo 'service freeradius stop'
    cd ${shelldir}
    echo ${shelldir}
    #mysqladmin -u root -p create radius
    #mysql -u root -p radius < /usr/local/etc/raddb/sql/mysql/schema.sql
    #mysql -u root -p radius < /usr/local/etc/raddb/sql/mysql/nas.sql
    #mysql -u root -p radius < /usr/local/etc/raddb/sql/mysql/ippool.sql
    #mysql -u root -p radius < /usr/local/etc/raddb/sql/mysql/wimax.sql
    #mysql -u root -p < ../radius/radius.sql
    cp ../radius/default /usr/local/etc/raddb/sites-enabled/
    cp ../radius/inner-tunnel /usr/local/etc/raddb/sites-enabled/
    cp ../radius/sql.conf /usr/local/etc/raddb/
    cp ../radius/radiusd.conf /usr/local/etc/raddb/
    cp ../radius/users /usr/local/etc/raddb/
    cp ../radius/dictionary /usr/local/etc/raddb/
    cp ../radius/clients.conf /usr/local/etc/raddb/
    cp ../radius/dialup.conf /usr/local/etc/raddb/sql/mysql/
    cp ../radius/counter.conf /usr/local/etc/raddb/sql/mysql/
	
	echo  ' test  radiusd -X'
	echo 'radtest vpn themass localhost 1812 testing123'
	echo 'service freeradius stop'
	
	#https://blog.csdn.net/laoxiao1987/article/details/16980147
	#http://www-2w.blog.163.com/blog/static/979315182011930114916789/
	#http://wiki.freeradius.org/guide/FAQ
	#ln -s /usr/local/mysql/bin/mysql_config /usr/local/bin/mysql_config
	# vi /etc/ld.so.conf  find  / -name libmysqlclient*    ldconfig
}
init_radius_client() {
	rm /usr/local/etc/raddb/clients.conf
	cp ../radius/clients.conf /usr/local/etc/raddb/
	sh radiusd.sh stop
	sh radiusd.sh start
}
setup_rclocal() {
	cp ../monitor/rc-local.service /etc/systemd/system/
	cp ../monitor/rc.local /etc/
	chmod +x /etc/rc.local
}

###
# influxdb 先设置密码，再打开鉴权#CREATE USER admin WITH PASSWORD 'themass529696'
#GRANT ALL PRIVILEGES TO admin
#create DATABASE telegraf
# CREATE RETENTION POLICY "10_day" ON "telegraf" DURATION 10d REPLICATION 1 DEFAULT
#create DATABASE vpn_monitor
#CREATE RETENTION POLICY "10_day" ON "vpn_monitor" DURATION 10d REPLICATION 1 DEFAULT
#influx -username 'admin' -password 'themass529696'
# vi /etc/influxdb/influxdb.conf  -->auth-enabled = true

###
setup_influx()
{
	shelldir=`pwd`
	cd ${TMP_HOME}
	rm ${TMP_HOME}/chronograf_1.3.9.0_amd64.deb
	rm ${TMP_HOME}/influxdb_1.3.6_amd64.deb
	rm ${TMP_HOME}/grafana_4.5.2_amd64.deb 
	 
	mkdir -p /home/grafana
	mkdir -p /home/grafana/plugins
	chmod 777 -R /home/grafana
	mkdir -p /home/influxdb/
	chmod 777 -R /home/influxdb
	
	
	wget https://dl.influxdata.com/chronograf/releases/chronograf_1.3.9.0_amd64.deb
	sudo dpkg -i chronograf_1.3.9.0_amd64.deb
	wget https://dl.influxdata.com/influxdb/releases/influxdb_1.3.6_amd64.deb
	sudo dpkg -i influxdb_1.3.6_amd64.deb
	wget https://s3-us-west-2.amazonaws.com/grafana-releases/release/grafana_4.5.2_amd64.deb 
	sudo dpkg -i grafana_4.5.2_amd64.deb 
	
	cd ${shelldir}
	echo ${shelldir}
	
	cp ../monitor/influxdb.conf /etc/influxdb/
	cp ../monitor/grafana.ini /etc/grafana/
	service influxdb restart
	service grafana-server restart
	echo "注意设置influxdb 用户名密码"
	
}
setup_bbrplus()
{
	cd ${TMP_HOME}
	wget -N --no-check-certificate "https://raw.githubusercontent.com/themass/Linux-NetSpeed/master/tcp.sh"
	chmod +x tcp.sh
	./tcp.sh
}

## -----------------------
## Show help message
## -----------------------
usage() 
{
    echo "Available arguments as below:"
    echo "user          Setup user"
    echo "mysql          Setup mysql"
    echo "kernel          Setup kernel"
    echo "check          Setup check"
    echo "radius_client          Setup radius_client"
    echo "influx          Setup setup_influx"
     echo "rclocal          Setup rc.local"
    echo "all           Setup all aboves"
    echo "bbrplus        Setup bbrplus"
}
setup_all()
{
	setup_mysql
	setup_kernel
	setup_radius
	setup_influx
}
## =====================================
## The main process
## =====================================
if [ $# != 0 ]; then
    for arg in $*; do
        case "$arg" in
			mysql)          setup_mysql;;
			mysql)          setup_mysql;;
			kernel)          setup_kernel;;
			check)          setup_check;;
			radius)         setup_radius;;
			influx)         setup_influx;;
			radius_client)         init_radius_client;;
			rclocal)         setup_rclocal;;
			all)          setup_all;;
			bbrplus)      setup_bbrplus;;
        esac
    done
else
    usage
fi
