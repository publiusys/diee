#!/bin/bash

export MQPS=${MQPS:="1000"}
export NITERS=${NITERS:='1'}
export MITR=${MITR:-""}
export MDVFS=${MDVFS:-""}
## c6220 MDVFS limits: 0c00 - 1a00
export AGENTS=${AGENTS:-"10.10.1.4,10.10.1.2,10.10.1.3"}
export TBENCH_SERVER=${TBENCH_SERVER:-"10.10.1.1"}

function runStatic
{
    echo ${TBENCH_SERVER} ${MQPS} ${MITR} ${MDVFS}

    ## start power logging
    ssh ${TBENCH_SERVER} sudo systemctl stop rapl_log
    ssh ${TBENCH_SERVER} sudo rm /data/rapl_log.log
    ssh ${TBENCH_SERVER} sudo systemctl restart rapl_log

    python mcd.py --qps ${MQPS} --itr ${MITR} --dvfs ${MDVFS}

    ## stop power logging
    ssh ${TBENCH_SERVER} sudo systemctl stop rapl_log
    
    name="qps${MQPS}_itr${MITR}_dvfs${MDVFS}"
    scp -r ${TBENCH_SERVER}:/data/rapl_log.log server_rapl_${name}.log
    mv mutilate.out mutilate_${name}.out

    #head -n 2 mutilate_${name}.out
    #python getavgenergy.py server_rapl_${name}.log
}

function runDynamic
{
    echo ${TBENCH_SERVER} ${MQPS} ${MITR} ${MDVFS} ${AGENTS}

    ## start power logging
    ssh ${TBENCH_SERVER} sudo systemctl stop rapl_log
    ssh ${TBENCH_SERVER} sudo rm /data/rapl_log.log
    ssh ${TBENCH_SERVER} sudo systemctl restart rapl_log

    python mcd.py --qps ${MQPS} --server ${TBENCH_SERVER} --agents ${AGENTS}

    ssh ${TBENCH_SERVER} sudo systemctl stop rapl_log
    name="qps${MQPS}_itr${MITR}_dvfs${MDVFS}"
    scp -r ${TBENCH_SERVER}:/data/rapl_log.log server_rapl_${name}.log
    mv mutilate.out mutilate_${name}.out

    python getavgenergy.py server_rapl_${name}.log
    cat mutilate_${name}.out | grep QPS
    cat mutilate_${name}.out | grep read
    
    #rsync --mkpath -avz *.log don:/home/handong/cloudlab/c6220/mcd/linux_dynamic/
    #rsync --mkpath -avz *.out don:/home/handong/cloudlab/c6220/mcd/linux_dynamic/
}

$@
