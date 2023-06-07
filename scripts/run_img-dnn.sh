#! /bin/bash

currdate=`date +%m_%d_%Y_%H_%M_%S`
#set -x

export MQPS=${MQPS:-"1000"}
export NITERS=${NITERS:='1'}
export WARMUP=${WARMUP:-"5000"}
export MAXQ=${MAXQ:-"20000"}
export MITR=${MITR:-"2"}
export MDVFS=${MDVFS:-"0c00"}

function runLinuxStatic
{
    echo "********************** runLinuxStatic **********************"
    for qps in ${MQPS}; do
	for itr in ${MITR}; do
	    for dvfs in ${MDVFS}; do
		echo "### python img-dnn.py --qps ${qps} --warmup ${WARMUP} --maxq ${MAXQ} --itr ${itr} --dvfs ${dvfs} ###"

		## start power logging
		ssh ${TBENCH_SERVER} sudo systemctl stop rapl_log
		ssh ${TBENCH_SERVER} sudo rm /data/rapl_log.log
		ssh ${TBENCH_SERVER} sudo systemctl restart rapl_log
		
		python img-dnn.py --qps ${qps} --warmup ${WARMUP} --maxq ${MAXQ} --itr ${itr} --dvfs ${dvfs}

		## stop power logging
		ssh ${TBENCH_SERVER} sudo systemctl stop rapl_log

		## retrieve logs
		#scp -r ${TBENCH_SERVER}:/data/rapl_log.log rapl_${i}_${qps}.log
		#python ~/bayop/tailbench/utilities/parselats.py lats.bin > lats_${i}_${qps}.log
		#mv lats.bin lats_${i}_${qps}.bin
		#rm lats.txt
		
		#mv rapl_${i}_${qps}.log ${currdate}
		#mv lats_${i}_${qps}.log ${currdate}
		#mv lats_${i}_${qps}.bin ${currdate}

		scp -r ${TBENCH_SERVER}:/data/rapl_log.log server_rapl_log.log
		cat server_rapl_log.log
		python ~/bayop/tailbench/utilities/parselats.py lats.bin
		rm lats.bin lats.txt
		echo "########################################################"
		echo ""
	    done
	done
    done
    echo "*********** runLinuxStatic FINISHED *************"
}

function runLinuxDynamic
{
    echo "********************** runLinuxDynamic **********************"
    echo "mkdir ${currdate}"
    #mkdir ${currdate}

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
	    #scp -r ${TBENCH_SERVER}:/data/rapl_log.log rapl_${i}_${qps}.log
	    #python ~/bayop/tailbench/utilities/parselats.py lats.bin > lats_${i}_${qps}.log
	    #mv lats.bin lats_${i}_${qps}.bin
	    #rm lats.txt

	    #mv rapl_${i}_${qps}.log ${currdate}
	    #mv lats_${i}_${qps}.log ${currdate}
	    #mv lats_${i}_${qps}.bin ${currdate}
	    
	    scp -r ${TBENCH_SERVER}:/data/rapl_log.log server_rapl_log.log
	    cat server_rapl_log.log
	    python ~/bayop/tailbench/utilities/parselats.py lats.bin
	    rm lats.bin lats.txt
	    echo "########################################################"
	    echo ""
	done
    done
    echo "*********** ${currdate} FINISHED *************"
}

"$@"
