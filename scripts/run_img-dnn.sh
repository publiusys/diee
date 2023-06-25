#!/bin/bash

currdate=`date +%m_%d_%Y_%H_%M_%S`
#set -x

export MQPS=${MQPS:="1000"}
export NITERS=${NITERS:='1'}
export MITR=${MITR:-"2"}
export MDVFS=${MDVFS:-"0c00"}
## xl170 MDVFS limits: 0c00 - 1800
export CLIENT1=${CLIENT1:-"192.168.1.1"}
export TBENCH_SERVER=${TBENCH_SERVER:-"192.168.1.20"}



function runOne
{
    echo ${TBENCH_SERVER} ${MQPS} ${MITR} ${MDVFS} ${CLIENT1}
    
    ## start power logging
    ssh ${TBENCH_SERVER} sudo systemctl stop rapl_log
    ssh ${TBENCH_SERVER} sudo rm /data/rapl_log.log
    ssh ${TBENCH_SERVER} sudo systemctl restart rapl_log

    MAXQ=$((MQPS*30))
    
    python img-dnn.py --qps ${MQPS} --warmup ${MQPS} --maxq ${MAXQ} --itr ${MITR} --dvfs ${MDVFS}

    name="qps${MQPS}_itr${MITR}_dvfs${MDVFS}"
    
    ## stop power logging
    ssh ${TBENCH_SERVER} sudo systemctl stop rapl_log
    
    scp -r ${TBENCH_SERVER}:/data/rapl_log.log server_rapl_${name}.log
    #wc -l server_rapl_log.log
    #cat server_rapl_log.log
    
    scp -r ${CLIENT1}:~/lats.bin client1lats_${name}.bin
    python ~/bayop/tailbench/utilities/parselats.py client1lats_${name}.bin > client1lats_${name}.txt
    mv lats.txt lats_${name}.txt
}

function runLinuxStatic
{
    echo "********************** runLinuxStatic **********************"
    for qps in ${MQPS}; do
	for itr in ${MITR}; do
	    for dvfs in ${MDVFS}; do
		MAXQ=$((qps*30))
		echo "### python img-dnn.py --qps ${qps} --warmup ${qps} --maxq ${MAXQ} --itr ${itr} --dvfs ${dvfs} ###"
		
		## start power logging
		ssh ${TBENCH_SERVER} sudo systemctl stop rapl_log
		ssh ${TBENCH_SERVER} sudo rm /data/rapl_log.log
		ssh ${TBENCH_SERVER} sudo systemctl restart rapl_log
		
		python img-dnn.py --qps ${qps} --warmup ${qps} --maxq ${MAXQ} --itr ${itr} --dvfs ${dvfs}
		
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
		wc -l server_rapl_log.log
		cat server_rapl_log.log
		
		scp -r ${CLIENT1}:~/lats.bin client1lats.bin
		python ~/bayop/tailbench/utilities/parselats.py client1lats.bin
		rm client1lats.bin lats.txt
		
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
	    MAXQ=$((qps*30))
	    echo "### ${i} python img-dnn.py --qps ${qps} --warmup ${qps} --maxq ${MAXQ} ###"
	    echo ""
	    
	    name="qps${qps}_niter${i}"
	    
	    ## start power logging
	    ssh ${TBENCH_SERVER} sudo systemctl stop rapl_log
	    ssh ${TBENCH_SERVER} sudo rm /data/rapl_log.log
	    ssh ${TBENCH_SERVER} sudo systemctl restart rapl_log

	    python img-dnn.py --qps ${qps} --warmup ${qps} --maxq ${MAXQ}

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

	    scp -r ${TBENCH_SERVER}:/data/rapl_log.log server_rapl_${name}.log
	    
	    scp -r ${CLIENT1}:~/lats.bin client1lats_${name}.bin
	    python ~/bayop/tailbench/utilities/parselats.py client1lats_${name}.bin > client1lats_${name}.txt
	    mv lats.txt lats_${name}.txt
    
	    #scp -r ${TBENCH_SERVER}:/data/rapl_log.log server_rapl_log.log
	    #cat server_rapl_log.log

	    #python ~/bayop/tailbench/utilities/parselats.py lats.bin
	    #rm lats.bin lats.txt

	    #scp -r ${CLIENT1}:~/lats.bin client1lats.bin
	    #python ~/bayop/tailbench/utilities/parselats.py client1lats.bin
	    #rm client1lats.bin lats.txt
	    echo "########################################################"
	    echo ""
	done
    done
    echo "*********** ${currdate} FINISHED *************"
}

$@
