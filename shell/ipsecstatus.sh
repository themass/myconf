#!/bin/bash
## -----------------------
## Version setting
## -----------------------
. /etc/profile
status() 
{
	/usr/sbin/ipsec status | grep Associations 
}
stop() 
{
	ps -ef |grep ipsec |awk '{print $2}' | xargs kill -9
}
restart() 
{
	/usr/sbin/ipsec restart
}
status_send() 
{
	c=`/usr/sbin/ipsec status | grep Associations | awk -F '(' '{print$2}' |awk -F' up' '{print$1}'`
	local_host=`/bin/hostname`
	 if [ -n "${c}" ]; then
	 	curl  -d "count=${c}"  -d "localhost=${local_host}" http://api.sspacee.com/vpn/api/noapp/collect.json
	 	echo ${local_host}
	 fi
}
usage() 
{
    echo "Available arguments as below:"
    echo "start           start"
    echo "stop          stop"
    echo "status          status"
    echo "status_send          status_send"
}
## =====================================
## The main process
## =====================================
if [ $# != 0 ]; then
    for arg in $*; do
        case "$arg" in
            start)            restart;;
            stop)          stop;;
            status)          status;;
            status_send)          status_send;;
        esac
    done
else
    usage
fi