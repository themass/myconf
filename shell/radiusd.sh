
#!/bin/bash
## -----------------------
## Version setting
## -----------------------

restart() 
{
	pkill -9 radiusd
	radiusd &
}
stop() 
{
	pkill -9 radiusd
}
debug() 
{
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
