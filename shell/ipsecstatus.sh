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
get_ip()
{
    local IP=$( ip addr | egrep -o '[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}' | egrep -v "^192\.168|^172\.1[6-9]\.|^172\.2[0-9]\.|^172\.3[0-2]\.|^10\.|^127\.|^255\.|^0\." | head -n 1 )
    [ -z ${IP} ] && IP=$( wget -qO- -t1 -T2 ipv4.icanhazip.com )
    [ -z ${IP} ] && IP=$( wget -qO- -t1 -T2 ipinfo.io/ip )
    [ ! -z ${IP} ] && echo ${IP} 
    echo ${IP}
}
status_send() 
{
	c=`/usr/sbin/ipsec status | grep Associations | awk -F '(' '{print$2}' |awk -F' up' '{print$1}'`
	local_host=`/bin/hostname`
	local_ip=$(get_ip)
	 if [ -n "${c}" ]; then
	 	curl  -d "count=${c}"  -d "localhost=${local_host}&ip=${local_ip}" -H"host=api.sspacee.com" http://47.88.7.156/vpn/api/noapp/collect.json
	 	echo ${local_host}
	 else
	  	curl  -d "count=-1"  -d "localhost=${local_host}&ip=${local_ip}" -H"host=api.sspacee.com" http://47.88.7.156/vpn/api/noapp/collect.json
	 	echo 'error restart'
	 	sudo reboot
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