#!/bin/bash
## -----------------------
## Version setting
## -----------------------
URL=http://10.117.233.81
APP_HOME=/root/local
TMP_HOME=/root/soft
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

mkdir -p ${APP_HOME}
mkdir -p ${TMP_HOME}

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
setup_user() {
 	useradd -r -m -s /bin/bash web
 	passwd web  
 	chmod u+w /etc/sudoers
 	vi  /etc/sudoers
 	#root ALL=(ALL) ALL
 	su - work
 	mkdir local
 	mkdir  webroot 
 	mkdir -p var/log 

}
setup_nginx() {
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
#    rm -rf ${APP_HOME}/nginx
#    ln -s ${APP_HOME}/${NGINX_VERSION} ${APP_HOME}/nginx
#    rm -rf ${APP_HOME}/nginx/html
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
    echo "user          Setup user"
    echo "all           Setup all aboves"
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
			user)          setup_user;;
			nginx)          setup_nginx;;
			all)          setup_all;;
        esac
    done
else
    usage
fi
