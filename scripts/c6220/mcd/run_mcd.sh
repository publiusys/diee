#!/bin/bash

currdate=`date +%m_%d_%Y_%H_%M_%S`

export BEGIN_ITER=${BEGIN_ITER:="0"}
export MQPS=${MQPS:="100000 200000 300000 400000 500000 600000"}
export NITERS=${NITERS:="2"}
export MITR=${MITR:="2 50 100 150 200 250 300 350 400 450 500 550 600 650 700 750 800 850 900 950 1000"}
export MDVFS=${MDVFS:="0c00 0d00 0e00 0f00 1000 1100 1200 1300 1400 1500 1600 1700 1800 1900 1a00"}
## c6220 MDVFS limits: 0c00 - 1a00
export AGENTS=${AGENTS:-"10.10.1.4,10.10.1.2,10.10.1.3"}
export TBENCH_SERVER=${TBENCH_SERVER:-"10.10.1.1"}

function runStatic
{
    echo "[INFO] START: ${currdate}"
    echo "[INFO] Input: DVFS ${MDVFS}"
    echo "[INFO] Input: ITRS ${MITR}"
    echo "[INFO] Input: NITERS ${NITERS}"
    echo "[INFO] Input: MQPS ${MQPS}"    

    #echo ${TBENCH_SERVER} ${MQPS} ${MITR} ${MDVFS}
    
    for i in `seq ${BEGIN_ITER} 1 ${NITERS}`; do
	for qps in ${MQPS}; do	    
	    for itr in ${MITR}; do
		for dvfs in ${MDVFS}; do
		    name="qps${qps}_itr${itr}_dvfs${dvfs}_${i}"
		    echo "-----------------------------------------------------------"
		    echo "[INFO] Run ${name}"
		    
		    echo "[INFO] python mcd.py --qps ${qps} --itr ${itr} --dvfs ${dvfs} --server ${TBENCH_SERVER} --agents ${AGENTS}"
		    python -u mcd.py --qps ${qps} --itr ${itr} --dvfs ${dvfs} --server ${TBENCH_SERVER} --agents ${AGENTS}
		    
		    mkdir ${name}
		    mv mutilate.out ${name}/
		    scp -r ${TBENCH_SERVER}:~/mcd.log.* ${name}/
		    
		    scp -r ${name} kd:/mnt/appavoo-data/data2/handong/mcdNN/
		    rm -rf ${name}
		    echo "[INFO] FINISHED"
		    echo "-----------------------------------------------------------"
		    echo ""
		done
	    done
	done
    done
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
