#!/bin/bash
## -----------------------
## Version setting
## -----------------------

## -----------------------
## Setup MySQL
## -----------------------
 start() {
 	mkdir -p /var/log/mysql/
  mkdir -p /var/run/mysqld
  chown mysql:mysql /var/log/mysql/
  chown mysql:mysql /var/run/mysqld
  mysqld_safe &
  radiusd &
  cd /root/local/nginx/sbin
  ./nginx

  su - web
  cd /home/web/local/redis-6.2.6/src
  ./redis-server ../redis.conf &
  cd /home/web/local/apache-tomcat-8.5.85/bin/
  ./startup.sh
}
## -----------------------
## Show help message
## -----------------------
usage() {
    echo "Available arguments as below:"
    echo "start           Setup start"

}
## =====================================
## The main process
## =====================================
if [ $# != 0 ]; then
    for arg in $*; do
        case "$arg" in
            start)          start;;
            *)              usage;;
        esac
    done
else
    usage
fi

