
#!/bin/bash
## -----------------------
## Version setting
## -----------------------
restart() 
{
	ps -ef |grep freeradius |awk '\''{print $2}'\'' | xargs kill -9
	pkill -9 radiusd
	radiusd &
}
stop() 
{
	ps -ef |grep freeradius |awk '\''{print $2}'\'' | xargs kill -9
	pkill -9 radiusd
}
debug() 
{
	ps -ef |grep freeradius |awk '\''{print $2}'\'' | xargs kill -9
	pkill -9 radiusd
	radiusd -X
}
usage() 
{
    echo "Available arguments as below:"
    echo "start           start"
    echo "stop          stop"
    echo "debug          debug"
}

## =====================================
## The main process
## =====================================
if [ $# != 0 ]; then
    for arg in $*; do
        case "$arg" in
            start)            restart;;
            stop)          stop;;
            debug)          debug;;
        esac
    done
else
    usage
fi