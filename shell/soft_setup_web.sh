#!/bin/bash
## -----------------------
## Version setting
## -----------------------

MYSQL_VERSION=mysql-5.6.34-linux-glibc2.5-x86_64
RADIUS_VERSION=freeradius-server-2.1.12

PHP_VERSION=php-7.1.12
REDIS_VERSION=redis-3.2.6

PWD=`pwd`

APP_HOME=/home/web/local
WEB_HOME=/home/web/webroot
TMP_HOME=/home/web/soft

mkdir -p /home/web/local
mkdir -p /home/web/soft
mkdir -p /home/web/work
#init soft
## -----------------------
## Setup JDK
## -----------------------
setup_jdk() {
  #https://www.oracle.com/java/technologies/javase/javase8u211-later-archive-downloads.html
  #mvn clean install -Ppro

  echo "。profile and java - version"


#	sudo add-apt-repository ppa:webupd8team/java
#	sudo apt-get update
#	sudo apt-get install oracle-java8-installer
#	sudo apt-get install oracle-java8-set-default
#	sudo sudo update-java-alternatives -s java-8-oracle
#	sudo java -version
#	sudo which java
	#　update-alternatives --config java
	#修改path

}

setup_maven(){
  cd /home/web/soft
  wget https://dlcdn.apache.org/maven/maven-3/3.8.8/binaries/apache-maven-3.8.8-bin.tar.gz --no-check-certificate
  tar -zxvf apache-maven-3.8.8-bin.tar.gz
  cd /home/web/local
   mv ../soft/apache-maven-3.8.8 .
   echo " mod .profile"

}
setup_redis() 
{
#http://download.redis.io/releases/redis-4.0.10.tar.gz
  cd /home/web/local
  wget http://download.redis.io/releases/redis-6.2.6.tar.gz
  tar -zxvf redis-6.2.6.tar.gz
  cd redis-6.2.6
  make
  cp ../../soft/myconf/redis/redis.conf  .
  cd src
  ./redis-server ../redis.conf  &


}

strongswan_android() 
{
	#https://wiki.strongswan.org/issues/652
	#libtool gperf
	#https://wiki.strongswan.org/projects/strongswan/wiki/AndroidVPNClientBuild
#	libstrongswan: aes des rc2 sha2 sha1 md5 random nonce x509 revocation constraints pubkey pkcs1 pkcs7 pkcs8 pkcs12 pgp dnskey sshkey pem fips-prf gmp curve25519 xcbc cmac hmac
#	libcharon:     attr kernel-netlink resolve socket-default stroke vici updown xauth-generic
#	libtnccs:
#   必须看 https://wiki.strongswan.org/projects/strongswan/repository/revisions/853cc61c2f818e1b513eef1c7467b94acbdeb19e/diff/src/libstrongswan/Android.mk
#
	#apt-get install flex bison libtool autoconf gperf gettext automake
	cd
	cd work
	rm -rf strongswan
	git clone git://git.strongswan.org/strongswan.git
	cd strongswan
	./autogen.sh 
	# eap+sha
	./configure 
	#--disable-curve25519
	make dist
	cd src/frontends/android/app/src/main/jni
	#git clone git://git.strongswan.org/android-ndk-openssl.git -b ndk-static openssl
	#ln -s ../../../../../../../../strongswan/  strongswan
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
setup_php()
{
	
	shelldir=`pwd`
	cd ${TMP_HOME}
	wget http://www.bzip.org/1.0.6/bzip2-1.0.6.tar.gz
	tar -zxvf  bzip2-1.0.6.tar.gz
	cd bzip2-1.0.6
	make 
	sudo make install
	echo 'makefile -fPIC'
	cd ..
	wget http://zlib.net/zlib-1.2.11.tar.gz
	tar -zxvf zlib-1.2.11.tar.gz
	cd zlib-1.2.11
	./configure
	make 
	sudo make install
	echo 'makefile -fPIC'
	sudo apt-get install libcurl4-gnutls-dev  libvpx-dev libjpeg-dev libpng-dev libXpm-dev libfreetype6-dev  libmcrypt-dev libmhash-dev
	rm php-7.1.13.tar.bz2
	wget http://cn.php.net/distributions/php-7.1.13.tar.bz2
	tar -jxvf php-7.1.13.tar.bz2
	rm -rf ${APP_HOME}/php-7.1.13
	rm -rf ${APP_HOME}/php
	cd php-7.1.13
	
    #rm -f ${PHP_VERSION}.tar.bz2  
    #rm -rf ${PHP_VERSION}
    #rm -rf ${APP_HOME}/${PHP_VERSION}
    #wget ${URL}/soft/${PHP_VERSION}.tar.bz2  
    #tar -jxvf ${PHP_VERSION}.tar.bz2  
    #cd ${PHP_VERSION}
    
    
    ./configure --prefix=/home/web/local/php-7.1.13 --with-config-file-path=${APP_HOME}/php-7.1.13/etc \
    --with-curl --with-pear --with-gd --with-jpeg-dir --with-vpx-dir --with-png-dir \
    --with-zlib --with-xpm-dir --with-freetype-dir --with-mcrypt --with-mhash --with-mysql \
    --with-mysqli --enable-pdo --with-pdo-mysql --with-openssl  --enable-fpm --enable-exif --enable-wddx --enable-zip \
    --enable-bcmath -with-bz2 --enable-calendar --enable-ftp --enable-mbstring --enable-soap --enable-sockets --enable-shmop \
    --enable-dba --enable-sysvmsg --enable-sysvsem --enable-sysvshm --enable-debug --enable-maintainer-zts --enable-embed --with-pdo-mysql=mysqlnd \
    --with-mysqli=mysqlnd --with-mysql=mysqlnd  --enable-mysqlnd 

    make -j4
    make install
    cd ${APP_HOME}
    rm php
    ln -s  php-7.1.13 php
    #cp ${shelldir}/../php/php-fpm.conf ${APP_HOME}/php/etc
    #cp ${shelldir}/../php/php.ini ${APP_HOME}/php/etc
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
    echo "maven       Setup maven"
    echo "android       Setup android"
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
	strongswan_android
	setup_maven
}
## =====================================
## The main process
## =====================================
if [ $# != 0 ]; then
    for arg in $*; do
        case "$arg" in
            jdk)            setup_jdk;;
			redis)          setup_redis;;
			daloradius)         setup_daloradius;;
			php)         setup_php;;
			maven)         setup_maven;;
			all)          setup_all;;
        esac
    done
else
    usage
fi
