#!/bin/bash
## -----------------------
## Version setting
## -----------------------

#URL=http://10.117.233.81:9003
URL=http://file.sspacee.com


APP_HOME=/root/local
TMP_HOME=/root/soft

MYSQL_VERSION=mysql-5.6.34-linux-glibc2.5-x86_64
RADIUS_VERSION=freeradius-server-2.1.12

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
	#wget http://kernel.ubuntu.com/~kernel-ppa/mainline/v4.13.16/linux-headers-4.13.16-041316-generic_4.13.16-041316.201711240901_arm64.deb
	#wget http://kernel.ubuntu.com/~kernel-ppa/mainline/v4.13.16/linux-image-4.13.16-041316-generic_4.13.16-041316.201711240901_arm64.deb
	
	wget http://kernel.ubuntu.com/~kernel-ppa/mainline/v4.13.16/linux-headers-4.13.16-041316_4.13.16-041316.201711240901_all.deb
	wget http://kernel.ubuntu.com/~kernel-ppa/mainline/v4.13.16/linux-headers-4.13.16-041316-generic_4.13.16-041316.201711240901_arm64.deb
	wget http://kernel.ubuntu.com/~kernel-ppa/mainline/v4.13.16/linux-image-4.13.16-041316-generic_4.13.16-041316.201711240901_arm64.deb
	
	dpkg -i *.deb 
	echo "net.core.default_qdisc=fq" >> /etc/sysctl.conf
	echo "net.ipv4.tcp_congestion_control=bbr" >> /etc/sysctl.conf
	sysctl -p
	sysctl net.ipv4.tcp_available_congestion_control
	lsmod | grep bbr
	#grep menuentry /boot/grub/grub.cfg
	# /etc/default/grub GRUB_DEFAULT=0-》2
	#update-grub
	#reboot
}
setup_user() {
 	useradd -r -m -s /bin/bash web
 	useradd -r -m -s /bin/bash work
 	useradd -r -m -s /bin/bash mysql
 	passwd web  
 	passwd work  
 	passwd mysql  
 	chmod u+w /etc/sudoers
 	vi  /etc/sudoers
 	#root ALL=(ALL) ALL
 	su - work
 	mkdir -p local
 	mkdir -p webroot 
 	mkdir -p var/log 
 	mkdir -p var/run
 	mkdir -p soft 
 	su - web 
 	mkdir -p local
 	mkdir -p webroot 
 	mkdir -p var/log 
 	mkdir -p var/run
 	mkdir -p soft 
}
## -----------------------
## Setup MySQL
## -----------------------
setup_mysql() {
	shelldir=`pwd`
    useradd -r -m -s /bin/bash mysql
    cd ${TMP_HOME}
    rm -f ${MYSQL_VERSION}.tar.gz
    rm -rf ${APP_HOME}/${MYSQL_VERSION}
    rm -rf /home/mysql/db_data/*
    wget ${URL}/soft/${MYSQL_VERSION}.tar.gz
    cd ${APP_HOME}
    tar zxvf ${TMP_HOME}/${MYSQL_VERSION}.tar.gz
    rm -rf /home/mysql/mysql
    ln -s ${APP_HOME}/${MYSQL_VERSION} /home/mysql/mysql
    rm -rf /usr/local/mysql
    ln -s ${APP_HOME}/${MYSQL_VERSION} /usr/local/mysql
    cd /home/mysql/mysql
    chown -R mysql .
    chgrp -R mysql .
    mkdir -p /home/mysql/db_data
    chown mysql:mysql /home/mysql/db_data
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
    echo 'profile /usr/local/mysql/bin'
    cp /home/mysql/mysql/share/english/errmsg.sys  /usr/share/mysql/
    mysqld_safe  &
    #show variables like "%char%"; ->utf-8
    
}
setup_radius()
{
	shelldir=`pwd`
	apt-get install  freeradius-mysql
	cd ${TMP_HOME}
    rm -f ${RADIUS_VERSION}.tar.gz
    rm -rf ${APP_HOME}/${RADIUS_VERSION}
    rm -rf /usr/local/etc/raddb
    wget ${URL}/soft/${RADIUS_VERSION}.tar.gz
	tar -zxvf ${RADIUS_VERSION}.tar.gz
	cd ${RADIUS_VERSION}
	./configure 
	make
	make install
	cd ${shelldir}
	echo ${shelldir}
	mysqladmin -u root -p create radius
	mysql -u root -p radius < /usr/local/etc/raddb/sql/mysql/schema.sql
	mysql -u root -p radius < /usr/local/etc/raddb/sql/mysql/nas.sql
	mysql -u root -p radius < /usr/local/etc/raddb/sql/mysql/ippool.sql
	mysql -u root -p radius < /usr/local/etc/raddb/sql/mysql/wimax.sql
	mysql -u root -p < ../radius/radius.sql
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
}
init_radius_client()
{
	rm /usr/local/etc/raddb/clients.conf
	cp ../radius/clients.conf /usr/local/etc/raddb/
}

###
# influxdb 先设置密码，再打开鉴权
#CREATE USER admin WITH PASSWORD 'themass529696'
#GRANT ALL PRIVILEGES TO admin
# CREATE RETENTION POLICY "10_day" ON "telegraf" DURATION 10d REPLICATION 1 DEFAULT
#influx -username 'admin' -password 'themass529696'
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
	setup_telegraf
	
	
}

setup_telegraf()
{
	shelldir=`pwd`
	cd ${TMP_HOME}
	rm ${TMP_HOME}/telegraf_1.4.2-1_amd64.deb
	wget https://dl.influxdata.com/telegraf/releases/telegraf_1.4.2-1_amd64.deb
	sudo dpkg -i telegraf_1.4.2-1_amd64.deb
	cd ${shelldir}
	echo ${shelldir}
	
	cp ../monitor/telegraf.conf /etc/telegraf/
	service telegraf restart
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
    echo "telegraf          Setup telegraf"
    echo "all           Setup all aboves"
}
setup_all()
{
	setup_user
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
			user)          setup_user;;
			mysql)          setup_mysql;;
			mysql)          setup_mysql;;
			kernel)          setup_kernel;;
			check)          setup_check;;
			radius)         setup_radius;;
			influx)         setup_influx;;
			telegraf)         setup_telegraf;;
			radius_client)         init_radius_client;;
			all)          setup_all;;
        esac
    done
else
    usage
fi
