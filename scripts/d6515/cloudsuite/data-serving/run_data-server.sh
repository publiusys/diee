#!/bin/bash

currdate=`date +%m_%d_%Y_%H_%M_%S`
#set -x

export MQPS=${MQPS:="1000"}
export NITERS=${NITERS:='1'}
export MITR=${MITR:-""}
export MDVFS=${MDVFS:-""}
## xl170 MDVFS limits: 0c00 - 1800
export CLIENT1=${CLIENT1:-"192.168.1.1"}
export CLIENT2=${CLIENT2:-"192.168.1.2"}
export CLIENT3=${CLIENT3:-"192.168.1.3"}
export TBENCH_SERVER=${TBENCH_SERVER:-"192.168.1.20"}

function clean
{
    rm *.txt *.log *.bin
}

function runOneDynamic
{
    echo ${TBENCH_SERVER} ${MQPS} ${MITR} ${MDVFS}
    
    for i in `seq 0 1 $NITERS`; do
	## start power logging
	ssh ${TBENCH_SERVER} sudo systemctl stop rapl_log
	ssh ${TBENCH_SERVER} sudo rm /data/rapl_log.log
	ssh ${TBENCH_SERVER} sudo systemctl restart rapl_log
	
	python data-server.py --qps ${MQPS}
	
	name="i${i}_qps${MQPS}_itr${MITR}_dvfs${MDVFS}"
	## stop power logging
	ssh ${TBENCH_SERVER} sudo systemctl stop rapl_log
	
	scp -r ${TBENCH_SERVER}:/data/rapl_log.log server_rapl_${name}.log
	mv clientOut.log client1lats_${name}.txt
    done
    
    #rsync --mkpath -avz *.log don:/home/handong/cloudlab/xl170/img-dnn/linux_dynamic/
    #rsync --mkpath -avz *.txt don:/home/handong/cloudlab/xl170/img-dnn/linux_dynamic/
    #rsync --mkpath -avz *.bin don:/home/handong/cloudlab/xl170/img-dnn/linux_dynamic/
}

function runOneStatic
{
    echo ${TBENCH_SERVER} ${MQPS} ${MITR} ${MDVFS} ${CLIENT1}
    
    ## start power logging
    ssh ${TBENCH_SERVER} sudo systemctl stop rapl_log
    ssh ${TBENCH_SERVER} sudo rm /data/rapl_log.log
    ssh ${TBENCH_SERVER} sudo systemctl restart rapl_log
    
    python data-server.py --qps ${MQPS} --itr ${MITR} --dvfs ${MDVFS}
    name="qps${MQPS}_itr${MITR}_dvfs${MDVFS}"
    
    ## stop power logging
    ssh ${TBENCH_SERVER} sudo systemctl stop rapl_log
    
    scp -r ${TBENCH_SERVER}:/data/rapl_log.log server_rapl_${name}.log
    mv clientOut.log client1lats_${name}.txt
}

$@
