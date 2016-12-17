#!/bin/bash
## -----------------------
## Version setting
## -----------------------

run_root() 
{
	pkill -9 radiusd
	ps -ef |grep freeradius |awk '\''{print $2}'\'' | xargs kill -9
	ps -ef |grep apache2 |awk '\''{print $2}'\'' | xargs kill -9
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
	/home/web/local/apache-tomcat-7.0.73/bin/startup.sh
	/home/web/local/php/sbin/php-fpm
}
usage() 
{
    echo "Available arguments as below:"
    echo "root           run_root"
    echo "web          run_web"
}

## =====================================
## The main process
## =====================================
if [ $# != 0 ]; then
    for arg in $*; do
        case "$arg" in
            root)            run_root;;
            web)          run_web;;
        esac
    done
else
    usage
fi
