# args java_main java_name btrace
## -----------------------
## java proc
## -----------------------
java_proc()
{
	export LD_PRELOAD=/usr/local/lib/libtcmalloc.so
	export HEAPPROFILE=/tmp/test
	java $2
}
## -----------------------
## mem proc
## -----------------------
mem_proc()
{
	  pprof --text $JAVA_HOME/bin/java $2 | more
}
## -----------------------
## btrace proc
## -----------------------
btrace_proc()
{
	  btrace -cp ~/local/btrace/build `jps | grep  $2 | awk '{print$1}'` $3
}
## -----------------------
## Show help message
## -----------------------
usage() 
{
    echo "Available arguments as below:"
    echo "java           java process"
    echo "mem           mem use"
    echo "btrace           btrace"
}
## =====================================
## The main process
## =====================================
if [ $# != 0 ]; then
    for arg in $*; do
        case "$arg" in
            java)            java_proc;;
            mem)             mem_proc;;
            btrace)            btrace_proc;;
        esac
    done
else
    usage
fi