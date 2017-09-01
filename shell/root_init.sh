#!/bin/bash
## -----------------------
## Version setting
## -----------------------

run_root() 
{
	pkill -9 radiusd
	ps -ef |grep rad |awk '{print $2}' | xargs kill -9
	ps -ef |grep apache2 |awk '{print $2}' | xargs kill -9
	radiusd &
	mysqld_safe &
	ipsec start
	killall nginx
	/root/local/nginx/sbin/nginx
}
run_web() 
{
	su - web
	/home/web/local/nginx/sbin/nginx
	sh local/apache-tomcat-7.0.73/bin/startup.sh
	/home/web/local/php/sbin/php-fpm
	/home/web/local/redis-3.2.6/bin/redis-server /home/web/local/redis-3.2.6/redis.conf &
}
run_check()
{
	ps -aux|grep mysqld_safe |grep -v grep  
	ps -aux|grep nginx |grep -v grep
	ps -aux|grep free |grep -v grep
	ps -aux|grep ipsec |grep -v grep
	ps -aux|grep tomcat |grep -v grep
	ps -aux|grep redis |grep -v grep
}
usage() 
{
    echo "Available arguments as below:"
    echo "root           run_root"
    echo "web          run_web"
    echo "check          run_check"
}

## =====================================
## The main process
## =====================================
if [ $# != 0 ]; then
    for arg in $*; do
        case "$arg" in
            root)            run_root;;
            web)          run_web;;
            check)          run_check;;
        esac
    done
else
    usage
fi