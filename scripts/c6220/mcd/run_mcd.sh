#!/bin/bash

export MQPS=${MQPS:="1000"}
export NITERS=${NITERS:='1'}
export MITR=${MITR:-""}
export MDVFS=${MDVFS:-""}
## c6220 MDVFS limits: 0c00 - 1800
export CLIENT1=${CLIENT1:-"192.168.1.1"}
export TBENCH_SERVER=${TBENCH_SERVER:-"192.168.1.20"}

function runOne
{
    echo ${TBENCH_SERVER} ${MQPS} ${MITR} ${MDVFS} ${CLIENT1}

    ## start power logging
    ssh ${TBENCH_SERVER} sudo systemctl stop rapl_log
    ssh ${TBENCH_SERVER} sudo rm /data/rapl_log.log
    ssh ${TBENCH_SERVER} sudo systemctl restart rapl_log

    python mcd.py --qps ${MQPS}

    name="qps${MQPS}_itr${MITR}_dvfs${MDVFS}"
    scp -r ${TBENCH_SERVER}:/data/rapl_log.log server_rapl_${name}.log

    mv mutilate.out mutilate_${name}.out

    #rsync --mkpath -avz *.log don:/home/handong/cloudlab/c6220/mcd/linux_dynamic/
    #rsync --mkpath -avz *.out don:/home/handong/cloudlab/c6220/mcd/linux_dynamic/
}

$@
