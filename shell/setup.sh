#!/bin/bash
## -----------------------
## Version setting
## -----------------------

APP_HOME=/root/local
TMP_HOME=/root/soft

MYSQL_VERSION=mysql-server_5.7.14-1ubuntu14.04_amd64.deb-bundle

mkdir -p /root/soft
mkdir -p /root/local
mkdir -p /root/work

## -----------------------
## Setup MySQL
## -----------------------
 setup_mysql() {
 	groupadd mysql
    useradd -d /home/mysql -g mysql mysql
 	killall -TERM mysqld
 	apt-get install mysql-server-5.6 mysql-client-5.6
    #groupadd mysql
    #useradd -d /home/mysql -g mysql mysql
    #dpkg -l |grep mysql | awk '{print$2}'|xargs dpkg -P
    #mkdir -p /home/mysql/data
    #chown mysql /home/mysql/data
    #chgrp mysql /home/mysql/data
    #cd ${APP_DW_HOME}
    #rm -f *mysql*
    #rm -rf /var/lib/mysql*
    #rm -rf /etc/mysql*
    #wget ${URL}/store/${MYSQL_VERSION}.tar
    #tar xvf ${APP_DW_HOME}/${MYSQL_VERSION}.tar
   	#dpkg -i mysql-common_5.7.14-1ubuntu14.04_amd64.deb 
   	##wget ${URL}/setup/myconf/mysql/my.cnf -O /etc/mysql/my.cnf
   	#dpkg-preconfigure  mysql-community-server_5.7.14-1ubuntu14.04_amd64.deb
   	#dpkg -i mysql-community-client_5.7.14-1ubuntu14.04_amd64.deb
   	#dpkg -i libmysqlclient20_5.7.14-1ubuntu14.04_amd64.deb
   	#dpkg -i libmysqlclient-dev_5.7.14-1ubuntu14.04_amd64.deb
   	#dpkg -i libmysqld-dev_5.7.14-1ubuntu14.04_amd64.deb 
   	#dpkg -i mysql-client_5.7.14-1ubuntu14.04_amd64.deb
   	#dpkg -i mysql-common_5.7.14-1ubuntu14.04_amd64.deb
   	#sudo apt-get -f install
   	#
   	##wget ${URL}/setup/myconf/mysql/my.cnf -O /etc/mysql/my.cnf
   	#
   	#dpkg -i mysql-community-server_5.7.14-1ubuntu14.04_amd64.deb
   	#dpkg -i mysql-server_5.7.14-1ubuntu14.04_amd64.deb 
    #
    ##mv /etc/mysql/my.cnf /etc/mysql/my.cnf_bak
    
    
    whereis mysql
}
## -----------------------
## Setup mysql_set
## -----------------------
# mysql_setshell() {
##	use mysql
##	UPDATE user SET password=PASSWORD('vpn@5296') WHERE user='root'
##	FLUSH PRIVILEGES
##	quit
##	create user vpn
##	update user set password=password("vpn@5296") where user="vpn"
##	create database vpn
##	grant all on vpn.* to 'vpn'

#create database sspanel;
#create database radius;
#GRANT ALL ON radius.* TO 'root'@'%';
#GRANT ALL ON  sspanel.* TO 'root'@'%';
#GRANT ALL ON vpn.* TO 'root'@'%';
#GRANT ALL ON radius.* TO 'radius'@'%';
##	flush privileges
##	quit
#}
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
 	exit
 	su - web
 	mkdir -p local
 	mkdir -p webroot
 	mkdir -p var/log
 	mkdir -p var/run
 	mkdir -p soft
 	exit
}
## -----------------------
## Setup nginx
## -----------------------
setup_nginx() {
    apt-get install libssl1.0-dev
    cd ${TMP_HOME}
    rm -rf openssl
    git clone https://github.com/openssl/openssl
    cd openssl/
    ./config --with-openssl-includes=/root/soft/openssl --with-openssl-libraries=/root/soft/openssl
    cd ../
    rm pcre-8.39.tar.gz
    wget https://onboardcloud.dl.sourceforge.net/project/pcre/pcre/8.39/pcre-8.39.tar.gz --no-check-certificate
    tar -zxvf pcre-8.39.tar.gz

    rm -rf nginx-1.16.1.tar.gz
    rm -rf nginx-1.16.1
    wget http://nginx.org/download/nginx-1.16.1.tar.gz
    git clone https://github.com/openresty/redis2-nginx-module
    git clone https://github.com/openresty/srcache-nginx-module
    git clone https://github.com/openresty/set-misc-nginx-module
    git clone https://github.com/openresty/echo-nginx-module
    wget https://github.com/vision5/ngx_devel_kit/archive/refs/tags/v0.3.1.tar.gz --no-check-certificate
    git clone https://github.com/FRiCKLE/ngx_cache_purge
    git clone https://github.com/replay/ngx_http_consistent_hash
    git clone https://github.com/replay/ngx_http_php_session
    git clone https://github.com/Yongke/ngx_http_redis-0.3.7
    git clone http://github.com/FRiCKLE/ngx_slowfs_cache/
    tar -zxvf v0.3.1.tar.gz
    tar -zxvf nginx-1.16.1.tar.gz
    cd nginx-1.16.1/
./configure --prefix=/root/local/nginx-1.16.1 --with-http_stub_status_module   --with-http_ssl_module --with-cc-opt="-Wimplicit-fallthrough=0" --with-http_gzip_static_module --with-pcre=../pcre-8.39 --add-module=../redis2-nginx-module --add-module=../srcache-nginx-module --add-module=../ngx_devel_kit-0.3.1 --add-module=../ngx_cache_purge --add-module=../ngx_http_consistent_hash --add-module=../ngx_http_php_session --add-module=../ngx_slowfs_cache   --add-module=../set-misc-nginx-module
#    --with-http_ssl_module --with-openssl=/root/soft  --add-module=../ngx_http_redis-0.3.7  zlib
    make
    make install
    mkdir -p /root/local/nginx-1.16.1/logs/
    rm -rf /root/local/nginx
    ln -s /root/local/nginx-1.16.1 /root/local/nginx
    rm /root/local/nginx/conf/nginx.conf

    mkdir -p /home/file/nginx/cache/temp
    mkdir -p /home/file/nginx_cache/cache/body
    cd /root/local/nginx/conf/
    mkdir server
    cp /root/work/myconf/nginx-sample/nginx.conf  .
    cp /root/work/myconf/nginx-sample/nginx_check.conf  server/.
    cp /root/work/myconf/nginx-sample/upstream.conf server/.
    cp /root/work/myconf/nginx-sample/vpn.conf  server/.
    cd
}

## -----------------------
## Show help message
## -----------------------
usage() {
    echo "Available arguments as below:"
    echo "jdk           Setup JDK"
    echo "maven         Setup maven"
    echo "nginx         Setup nginx"
    echo "OpenResty     Setup OpenResty"
    echo "memcached     Setup memcached"
    echo "redis         Setup redis"
    echo "mysql         Setup MySQL"
    echo "mongodb       Setup MongoDB"
    echo "python        Setup Python 2.7.4"
    echo "rsync         Setup rsync 3.1.0"
    echo "tomcat        Setup tomcat 1.7"
    echo "all           Setup all aboves"
}

## =====================================
## The main process
## =====================================
if [ $# != 0 ]; then
    for arg in $*; do
        case "$arg" in
            nginx)          setup_nginx;;
	    	    mysql)	    setup_mysql;;
	    	    user)	    setup_user;;
            *)              usage;;
        esac
    done
else
    usage
fi

