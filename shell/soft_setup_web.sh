#!/bin/bash
## -----------------------
## Version setting
## -----------------------
URL=http://10.117.233.81:8080
APP_HOME=/home/web/local
WEB_HOME=/home/web/webroot
TMP_HOME=/home/web/soft
JDK_VERSION=jdk-8u111
JDK_DIR=jdk1.8

SDK_NAME_VERSION=android-sdk_r24.0.2-linux
SDK_VERSION=android-sdk-linux
SDK_PLATFORM_VERSION=platform-tools_r23.1.0-linux

SDK_PLATFORM_P_VERSION_1=android-17_r01
SDK_PLATFORM_P_VERSION_2=android-19_r03
SDK_PLATFORM_P_VERSION_3=android-21_r01
SDK_PLATFORM_P_VERSION_4=android-22_r02

SDK_PLATFORM_P_VERSION_P_1=android-4.2
SDK_PLATFORM_P_VERSION_P_2=android-4.4.2
SDK_PLATFORM_P_VERSION_P_3=android-5.0
SDK_PLATFORM_P_VERSION_P_4=android-5.1.1

SDK_PLATFORM_P_VERSION_P_P_1=android-17
SDK_PLATFORM_P_VERSION_P_P_2=android-19
SDK_PLATFORM_P_VERSION_P_P_3=android-21
SDK_PLATFORM_P_VERSION_P_P_4=android-22

NDK_VERSION=android-ndk64-r10b-linux-x86_64
MAVEN_VERSION=apache-maven-3.0.3
NGINX_VERSION=nginx-1.10.2
NGINX_REDIS_VERSION=ngx_http_redis-0.3.7
NGINX_REDIS2_VERSION=redis2-nginx-module-0.11
NGINX_SRCACHE_VERSION=srcache-nginx-module-0.26
NGINX_DEVEL_VERSION=ngx_devel_kit-0.2.19
NGINX_MISC_VERSION=set-misc-nginx-module-0.24
NGINX_SLOWFS_VERSION=ngx_slowfs_cache-1.10
NGINX_PURGE_VERSION=ngx_cache_purge
NGINX_PHP_VERSION=ngx_http_php_session-0.3
NGINX_ACCOUNTING_VERSION=ngx_http_accounting_module-0.2
NGINX_CONSISTENT_VERSION=ngx_http_consistent_hash
NGINX_ECHO_VERSION=echo-nginx-module
NGINX_PCRE_VERSION=pcre-8.39

MYSQL_VERSION=mysql-5.6.34-linux-glibc2.5-x86_64
RADIUS_VERSION=freeradius-server-2.1.12

PHP_VERSION=php-5.6.29

REDIS_VERSION=redis-3.2.6

mkdir -p ${APP_HOME}
mkdir -p ${TMP_HOME}
PWD=`pwd`

#init soft
setup_jdk() 
{
	cd ${APP_HOME}
    rm -f ${TMP_HOME}/${JDK_VERSION}.tar.gz
    rm -rf ${JDK_DIR}
    wget ${URL}/soft/${JDK_VERSION}.tar.gz -O ${TMP_HOME}/${JDK_VERSION}.tar.gz
    tar -zxvf ${TMP_HOME}/${JDK_VERSION}.tar.gz 
	echo 'profile' ${APP_HOME}/${JDK_VERSION}
}
setup_sdk() 
{
	cd ${APP_HOME}
	rm -f ${TMP_HOME}/${SDK_VERSION}.tgz
	rm -rf ${SDK_VERSION}
	wget ${URL}/soft/${SDK_NAME_VERSION}.tgz -O ${TMP_HOME}/${SDK_VERSION}.tgz
	tar -zxvf ${TMP_HOME}/${SDK_VERSION}.tgz 
	rm -rf ${TMP_HOME}/${SDK_PLATFORM_VERSION}.zip 
	wget ${URL}/soft/${SDK_PLATFORM_VERSION}.zip -O ${TMP_HOME}/${SDK_PLATFORM_VERSION}.zip
	unzip ${TMP_HOME}/${SDK_PLATFORM_VERSION}.zip
	mv platform-tools  ${SDK_VERSION}/
	
	rm -f ${TMP_HOME}/${SDK_PLATFORM_P_VERSION_1}.zip
	rm -f ${TMP_HOME}/${SDK_PLATFORM_P_VERSION_2}.zip
	rm -f ${TMP_HOME}/${SDK_PLATFORM_P_VERSION_3}.zip
	rm -f ${TMP_HOME}/${SDK_PLATFORM_P_VERSION_4}.zip
	
	wget ${URL}/soft/${SDK_PLATFORM_P_VERSION_1}.zip -O ${TMP_HOME}/${SDK_PLATFORM_P_VERSION_1}.zip
	wget ${URL}/soft/${SDK_PLATFORM_P_VERSION_2}.zip -O ${TMP_HOME}/${SDK_PLATFORM_P_VERSION_2}.zip
	wget ${URL}/soft/${SDK_PLATFORM_P_VERSION_3}.zip -O ${TMP_HOME}/${SDK_PLATFORM_P_VERSION_3}.zip
	wget ${URL}/soft/${SDK_PLATFORM_P_VERSION_4}.zip -O ${TMP_HOME}/${SDK_PLATFORM_P_VERSION_4}.zip
	
	unzip ${TMP_HOME}/${SDK_PLATFORM_P_VERSION_1}.zip  
	unzip ${TMP_HOME}/${SDK_PLATFORM_P_VERSION_2}.zip  
	unzip ${TMP_HOME}/${SDK_PLATFORM_P_VERSION_3}.zip  
	unzip ${TMP_HOME}/${SDK_PLATFORM_P_VERSION_4}.zip  
	mv ${SDK_PLATFORM_P_VERSION_P_1} ${SDK_VERSION}/platforms/${SDK_PLATFORM_P_VERSION_P_P_1}
	mv ${SDK_PLATFORM_P_VERSION_P_2} ${SDK_VERSION}/platforms/${SDK_PLATFORM_P_VERSION_P_P_2}
	mv ${SDK_PLATFORM_P_VERSION_P_3} ${SDK_VERSION}/platforms/${SDK_PLATFORM_P_VERSION_P_P_3}
	mv ${SDK_PLATFORM_P_VERSION_P_4} ${SDK_VERSION}/platforms/${SDK_PLATFORM_P_VERSION_P_P_4}
	
	echo 'profile' ${APP_HOME}/${SDK_VERSION} 
	
}
setup_ndk() 	
{
	cd ${APP_HOME}
	rm -f ${TMP_HOME}/${NDK_VERSION}.tgz
	rm -rf ${NDK_VERSION}
	wget ${URL}/soft/${NDK_VERSION}.tar.bz2 -O ${TMP_HOME}/${NDK_VERSION}.tar.bz2
	tar -jxvf ${TMP_HOME}/${NDK_VERSION}.tar.bz2
	echo 'profile' ${APP_HOME}/${NDK_VERSION}
}
setup_redis() 
{
	shelldir=`pwd`
	cd ${TMP_HOME}
	rm -rf ${APP_HOME}/${REDIS_VERSION}
    rm -f ${TMP_HOME}/${REDIS_VERSION}.tar.gz
    wget ${URL}/soft/${REDIS_VERSION}.tar.gz 
    tar -zxvf ${REDIS_VERSION}.tar.gz 
    cd ${REDIS_VERSION}
    make
    make PREFIX=${APP_HOME}/${REDIS_VERSION} install
    cp ${shelldir}/../redis/redis.conf  ${APP_HOME}/${REDIS_VERSION}/
	echo 'profile' ${APP_HOME}/${REDIS_VERSION}
}
setup_nginx() {
	shelldir=`pwd`
	cd ${TMP_HOME}
    rm -f ${NGINX_VERSION}.tar.gz
    rm -rf ${NGINX_VERSION}
    rm -rf ${APP_HOME}/${NGINX_VERSION}
    wget ${URL}/soft/nginx/${NGINX_VERSION}.tar.gz
    tar -zxvf ${NGINX_VERSION}.tar.gz
    
	rm -f ${NGINX_REDIS_VERSION}.tar.gz
    rm -rf ${NGINX_REDIS_VERSION}
    wget ${URL}/soft/nginx/${NGINX_REDIS_VERSION}.tar.gz
    tar zxvf ${NGINX_REDIS_VERSION}.tar.gz
    
    rm -f ${NGINX_REDIS2_VERSION}.tar.gz
    rm -rf ${NGINX_REDIS2_VERSION}
    wget ${URL}/soft/nginx/${NGINX_REDIS2_VERSION}.tar.gz
    tar zxvf ${NGINX_REDIS2_VERSION}.tar.gz
    
    rm -f ${NGINX_SRCACHE_VERSION}.tar.gz
    rm -rf ${NGINX_SRCACHE_VERSION}
    wget ${URL}/soft/nginx/${NGINX_SRCACHE_VERSION}.tar.gz
    tar zxvf ${NGINX_SRCACHE_VERSION}.tar.gz
    
    rm -f ${NGINX_DEVEL_VERSION}.tar.gz
    rm -rf ${NGINX_DEVEL_VERSION}
    wget ${URL}/soft/nginx/${NGINX_DEVEL_VERSION}.tar.gz
    tar zxvf ${NGINX_DEVEL_VERSION}.tar.gz
    
    rm -f ${NGINX_MISC_VERSION}.tar.gz
    rm -rf ${NGINX_MISC_VERSION}
    wget ${URL}/soft/nginx/${NGINX_MISC_VERSION}.tar.gz
    tar zxvf ${NGINX_MISC_VERSION}.tar.gz
    
    rm -f ${NGINX_SLOWFS_VERSION}.tar.gz
    rm -rf ${NGINX_SLOWFS_VERSION}
    wget ${URL}/soft/nginx/${NGINX_SLOWFS_VERSION}.tar.gz
    tar zxvf ${NGINX_SLOWFS_VERSION}.tar.gz
    
    rm -f ${NGINX_PURGE_VERSION}.tar.gz
    rm -rf ${NGINX_PURGE_VERSION}
    https://github.com/FRiCKLE/ngx_cache_purge.git
    
    
    rm -f ${NGINX_PHP_VERSION}.tar.gz
    rm -rf ${NGINX_PHP_VERSION}
    wget ${URL}/soft/nginx/${NGINX_PHP_VERSION}.tar.gz
    tar zxvf ${NGINX_PHP_VERSION}.tar.gz
    
    rm -f ${NGINX_ACCOUNTING_VERSION}.tar.gz
    rm -rf ${NGINX_ACCOUNTING_VERSION}
    wget ${URL}/soft/nginx/${NGINX_ACCOUNTING_VERSION}.tar.gz
    tar zxvf ${NGINX_ACCOUNTING_VERSION}.tar.gz
    
    rm -f ${NGINX_PCRE_VERSION}.tar.gz
    rm -rf ${NGINX_PCRE_VERSION}
    wget ${URL}/soft/nginx/${NGINX_PCRE_VERSION}.tar.gz
    tar -zxvf ${NGINX_PCRE_VERSION}.tar.gz
    
    rm -rf ${NGINX_ECHO_VERSION}
    git clone git://github.com/agentzh/echo-nginx-module.git
    
    rm -rf ${NGINX_CONSISTENT_HASH_VERSION}
    git clone https://github.com/replay/ngx_http_consistent_hash.git

	
    cd ${NGINX_VERSION}
	./configure --prefix=${APP_HOME}/${NGINX_VERSION} --with-http_stub_status_module --with-http_ssl_module --with-http_gzip_static_module \
	--with-pcre=../${NGINX_PCRE_VERSION}
	--add-module=../${NGINX_REDIS_VERSION} --add-module=../${NGINX_REDIS2_VERSION} --add-module=../${NGINX_SRCACHE_VERSION} \
	--add-module=../${NGINX_DEVEL_VERSION} --add-module=../${NGINX_PURGE_VERSION} --add-module=../${NGINX_SLOWFS_VERSION=} \
	--add-module=../${NGINX_PHP_VERSION} --add-module=../${NGINX_ACCOUNTING_VERSION} --add-module=../${NGINX_CONSISTENT_VERSION}  \
	--add-module=../${NGINX_CONSISTENT_VERSION} --add-module=../${NGINX_ECHO_VERSION}
	make -j4
    make install
    rm -rf ${APP_HOME}/nginx
    ln -s ${APP_HOME}/${NGINX_VERSION} ${APP_HOME}/nginx
    rm -rf ${APP_HOME}/nginx/html
    cd ${shelldir}
    rm ${APP_HOME}/nginx/conf/nginx.conf
    cp ../nginx/conf/nginx.conf ${APP_HOME}/nginx/conf/nginx.conf
    cp ../nginx/server ${APP_HOME}/nginx/conf/ -r

}
strongswan_android() 
{
	#https://wiki.strongswan.org/issues/652
	#libtool gperf
	#https://wiki.strongswan.org/projects/strongswan/wiki/AndroidVPNClientBuild
	apt-get install flex bison libtool autoconf gperf gettext automake
	cd
	cd work
	git clone git://git.strongswan.org/strongswan.git
	cd strongswan
	./autogen.sh 
	./configure 
	make dist
	cd src/frontends/android/app/src/main/jni
	git clone git://git.strongswan.org/android-ndk-openssl.git -b ndk-static jni/openssl
	ln -s ../../../../../../../../strongswan/  strongswan
	ndk-build
}
setup_daloradius()
{
	sudo apt-get install php5-common php5-gd php-pear php-db libapache2-mod-php5 php-mail php5-mysql
	
	cd ${TMP_HOME}
	wget http://nchc.dl.sourceforge.net/project/daloradius/daloradius/daloradius0.9-9/daloradius-0.9-9.tar.gz
	cd ${WEB_HOME}
	tar -zxvf ${TMP_HOME}/daloradius-0.9-9.tar.gz
	mv daloradius-0.9-9
	mysql -u root -p radius < daloradius-0.9-9/contrib/db/fr2-mysql-daloradius-and-freeradius.sql
	echo 'daloradius-0.9-9/library/daloradius.conf.php'
	echo '/home/web/local/php'
	pear upgrade-all
	pear install DB
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
setup_php()
{
	
	shelldir=`pwd`
	cd ${TMP_HOME}
	#wget http://www.bzip.org/1.0.6/bzip2-1.0.6.tar.gz
	#tar -zxvf  bzip2-1.0.6.tar.gz
	#cd bzip2-1.0.6
	#make 
	#sudo make install
	#echo 'makefile -fPIC'
	#cd ..
	#wget http://zlib.net/zlib-1.2.8.tar.gz
	#tar -zxvf zlib-1.2.8.tar.gz
	#cd zlib-1.2.8
	#make 
	#make install
	#echo 'makefile -fPIC'
	sudo apt-get install libcurl4-gnutls-dev  libvpx-dev libjpeg-dev libpng-dev libXpm-dev libfreetype6-dev  libmcrypt-dev libmhash-dev
    rm -f ${PHP_VERSION}.tar.bz2  
    rm -rf ${PHP_VERSION}
    rm -rf ${APP_HOME}/${PHP_VERSION}
    wget ${URL}/soft/${PHP_VERSION}.tar.bz2  
    tar -jxvf ${PHP_VERSION}.tar.bz2  
    cd ${PHP_VERSION}
    ./configure --prefix=${APP_HOME}/${PHP_VERSION} --with-config-file-path=${APP_HOME}/${PHP_VERSION}/etc \
    --with-curl --with-pear --with-gd --with-jpeg-dir --with-vpx-dir --with-png-dir \
    --with-zlib --with-xpm-dir --with-freetype-dir --with-mcrypt --with-mhash --with-mysql \
    --with-mysqli --enable-pdo --with-pdo-mysql --with-openssl  --enable-fpm --enable-exif --enable-wddx --enable-zip \
    --enable-bcmath -with-bz2 --enable-calendar --enable-ftp --enable-mbstring --enable-soap --enable-sockets --enable-shmop \
    --enable-dba --enable-sysvmsg --enable-sysvsem --enable-sysvshm --enable-debug --enable-maintainer-zts --enable-embed
    make -j4
    make install
    cd ${APP_HOME}
    ln -s  ${PHP_VERSION} php
    cp ${shelldir}/../php/php-fpm.conf ${APP_HOME}/php/etc
    cp ${shelldir}/../php/php.ini ${APP_HOME}/php/etc
    mkdir -p ${APP_HOME}/php/lib/php/extensions
    cd ${APP_HOME}/php/lib/php/extensions
    pear install DB
    echo 'killall php-fpm '
    echo 'profile php'
    
}
## -----------------------
## Show help message
## -----------------------
usage() 
{
    echo "Available arguments as below:"
    echo "jdk           Setup init jdk"
    echo "sdk          Setup sdk"
    echo "ndk          Setup ndk"
    echo "nginx          Setup nginx"
    echo "radius          Setup radius"
    echo "daloradius       Setup daloradius"
    echo "php       Setup php"
    echo "redis       Setup redis"
    echo "all           Setup all aboves"
}
setup_all()
{
	setup_jdk
	setup_sdk
	setup_ndk
	setup_nginx
	setup_php
	setup_redis
}
## =====================================
## The main process
## =====================================
if [ $# != 0 ]; then
    for arg in $*; do
        case "$arg" in
            jdk)            setup_jdk;;
            sdk)          setup_sdk;;
			ndk)          setup_ndk;;
			nginx)          setup_nginx;;
			redis)          setup_redis;;
			radius)         setup_radius;;
			daloradius)         setup_daloradius;;
			php)         setup_php;;
			all)          setup_all;;
        esac
    done
else
    usage
fi
