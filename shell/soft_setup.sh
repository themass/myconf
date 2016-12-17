#!/bin/bash
## -----------------------
## Version setting
## -----------------------
URL=http://10.117.233.81:9003
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
}
setup_kernel()
{
	cd ${TMP_HOME}
	rm -rm kernel
	mkdir kernel
	cd kernel
	wget wget ${URL}/soft/linux-kernel/linux-headers-4.9.0-040900_4.9.0-040900.201612111631_all.deb
	wget wget ${URL}/soft/linux-kernel/linux-headers-4.9.0-040900-generic_4.9.0-040900.201612111631_amd64.deb
	wget wget ${URL}/soft/linux-kernel/linux-image-4.9.0-040900-generic_4.9.0-040900.201612111631_amd64.deb
	dpkg -i *.deb 
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
    echo "all           Setup all aboves"
}
setup_all()
{
	setup_user
	setup_mysql
	setup_kernel
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
			all)          setup_all;;
        esac
    done
else
    usage
fi
