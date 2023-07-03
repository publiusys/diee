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
	
	MAXQ=$((3*MQPS*30))
	
	python img-dnn.py --qps ${MQPS} --warmup ${MQPS} --maxq ${MAXQ} --nclients 3
	
	name="i${i}_qps${MQPS}_itr${MITR}_dvfs${MDVFS}"
	## stop power logging
	ssh ${TBENCH_SERVER} sudo systemctl stop rapl_log
	
	scp -r ${TBENCH_SERVER}:/data/rapl_log.log server_rapl_${name}.log	
	scp -r ${CLIENT1}:~/lats.bin client1lats_${name}.bin
	python ~/bayop/tailbench/utilities/parselats.py client1lats_${name}.bin > client1lats_${name}.txt
	scp -r ${CLIENT2}:~/lats.bin client2lats_${name}.bin
	python ~/bayop/tailbench/utilities/parselats.py client2lats_${name}.bin > client2lats_${name}.txt
	scp -r ${CLIENT3}:~/lats.bin client3lats_${name}.bin
	python ~/bayop/tailbench/utilities/parselats.py client3lats_${name}.bin > client3lats_${name}.txt

	cat client*lats*.txt | grep 99th
	head -n 30 server_rapl_${name}.log | tail -n 20
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

    MAXQ=$((3*MQPS*30))    
    python img-dnn.py --qps ${MQPS} --warmup ${MQPS} --maxq ${MAXQ} --itr ${MITR} --dvfs ${MDVFS} --nclients 3
    name="qps${MQPS}_itr${MITR}_dvfs${MDVFS}"
    
    ## stop power logging
    ssh ${TBENCH_SERVER} sudo systemctl stop rapl_log
    
    scp -r ${TBENCH_SERVER}:/data/rapl_log.log server_rapl_${name}.log    
    scp -r ${CLIENT1}:~/lats.bin client1lats_${name}.bin
    python ~/bayop/tailbench/utilities/parselats.py client1lats_${name}.bin > client1lats_${name}.txt
    scp -r ${CLIENT2}:~/lats.bin client2lats_${name}.bin
    python ~/bayop/tailbench/utilities/parselats.py client2lats_${name}.bin > client2lats_${name}.txt
    scp -r ${CLIENT3}:~/lats.bin client3lats_${name}.bin
    python ~/bayop/tailbench/utilities/parselats.py client3lats_${name}.bin > client3lats_${name}.txt

    cat client*lats*.txt | grep 99th
    head -n 30 server_rapl_${name}.log | tail -n 20
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

$@
