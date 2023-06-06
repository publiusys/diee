#! /bin/bash

currdate=`date +%m_%d_%Y_%H_%M_%S`
#set -x

export MQPS=${MQPS:-"1000"}
export NITERS=${NITERS:='1'}
export WARMUP=${WARMUP:-"5000"}
export MAXQ=${MAXQ:-"20000"}

function runLinuxDefault
{
    echo "********************** runLinuxDefault **********************"
    echo "mkdir ${currdate}"
    mkdir ${currdate}

    for qps in ${MQPS}; do
	for i in `seq 0 1 $NITERS`; do
	    echo "### ${i} python img-dnn.py --qps ${qps} --warmup ${WARMUP} --maxq ${MAXQ} ###"
	    echo ""
	    
	    ## start power logging
	    ssh ${TBENCH_SERVER} sudo systemctl stop rapl_log
	    ssh ${TBENCH_SERVER} sudo rm /data/rapl_log.log
	    ssh ${TBENCH_SERVER} sudo systemctl restart rapl_log

	    python img-dnn.py --qps ${qps} --warmup ${WARMUP} --maxq ${MAXQ}

	    ## stop power logging
	    ssh ${TBENCH_SERVER} sudo systemctl stop rapl_log
	    #ssh ${TBENCH_SERVER} cat /data/rapl_log.log

	    ## retrieve logs
	    scp -r ${TBENCH_SERVER}:/data/rapl_log.log rapl_${i}_${qps}.log
	    python ~/bayop/tailbench/utilities/parselats.py lats.bin > lats_${i}_${qps}.log
	    mv lats.bin lats_${i}_${qps}.bin
	    rm lats.txt

	    mv rapl_${i}_${qps}.log ${currdate}
	    mv lats_${i}_${qps}.log ${currdate}
	    mv lats_${i}_${qps}.bin ${currdate}
	    
	    #tail -n 10 server_rapl_log.log
	    echo "########################################################"
	    echo ""
	done
    done
    echo "*********** ${currdate} FINISHED *************"
}

"$@"
