#!/bin/bash
## -----------------------
## Version setting
## -----------------------
APPPATH=/root/work/myconf/python/fetch
PROCESS_IDS=(dehyc.py se8_vip.py)
LOG_FILE=/var/log/fetch.log
start_process()
{
     echo "PROCESS_ID:" $1;
     echo "ENV:" $2;
     PROCESS_ID=$1
     cd ${APPPATH}

     id=`ps -ef|grep -v grep|grep -v start.sh|grep ${PROCESS_ID}|awk '{print $2}'`

    if [ -n "${id}" ]; then
	echo "${PROCESS_ID} is already running, PID is: ${id}, kill it...."
	kill ${id}
	sleep 3s
    fi

    id=`ps -ef|grep -v grep|grep -v start.sh|grep ${PROCESS_ID}|awk '{print $2}'`
    if [ -z "${id}" ]; then
	    nohup python ${APPPATH}/${PROCESS_ID} -e ${env} > ${LOG_FILE} &
	    echo "${PROCESS_ID} started."
    else
	echo "kill ${PROCESS_ID} failed , PID is: ${id}"
    fi
}

PROCESS_ID=''
for PROCESS_ID in "$@";do
    case $PROCESS_ID in
        se8|deh) PROCESS_ID="${PROCESS_ID} ";;
        *) echo "Please specify a env type: se8,deh";exit 1;;
    esac
done

if [ -z "${PROCESS_ID}" ]; then
  echo "Please specify a  type: deh,se8"
  exit 1
fi

start_process ${PROCESS_ID} prod