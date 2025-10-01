#!/bin/bash

currdate=`date +%m_%d_%Y_%H_%M_%S`

export BEGIN_ITER=${BEGIN_ITER:="0"}
export MQPS=${MQPS:="100000 200000 300000 400000 500000 600000"}
export NITERS=${NITERS:="3"}
export AGENTS=${AGENTS:-"10.10.1.1,10.10.1.2,10.10.1.3,10.10.1.4,10.10.1.5,10.10.1.6"}
export TBENCH_SERVER=${TBENCH_SERVER:-"10.10.1.7"}

function runDynamic
{
    mkdir -p dynamic
    
    echo ${TBENCH_SERVER} ${NITERS} ${MQPS} ${AGENTS}
    
    for (( i=$BEGIN_ITER; i<$NITERS; i++ )); do
	for qps in ${MQPS}; do
	    ## start power logging
	    ssh ${TBENCH_SERVER} sudo systemctl stop rapl_log
	    ssh ${TBENCH_SERVER} sudo rm /data/rapl_log.log
	    ssh ${TBENCH_SERVER} sudo systemctl restart rapl_log
	
	    python mcd.py --qps ${qps} --server ${TBENCH_SERVER} --agents ${AGENTS}
	    
	    ssh ${TBENCH_SERVER} sudo systemctl stop rapl_log
	    name="qps${qps}_iter${i}"
	    scp -r ${TBENCH_SERVER}:/data/rapl_log.log dynamic/server_rapl_${name}.log
	    mv mutilate.out dynamic/mutilate_${name}.out
	    
	    python getavgenergy.py dynamic/server_rapl_${name}.log
	    cat dynamic/mutilate_${name}.out | grep QPS
	    cat dynamic/mutilate_${name}.out | grep read
	done
	#rsync --mkpath -avz *.log don:/home/handong/cloudlab/c6220/mcd/linux_dynamic/
	#rsync --mkpath -avz *.out don:/home/handong/cloudlab/c6220/mcd/linux_dynamic/
    done
}

$@
