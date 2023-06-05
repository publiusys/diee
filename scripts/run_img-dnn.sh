#! /bin/bash

currdate=`date +%m_%d_%Y_%H_%M_%S`
set -x

export MQPS=${MQPS:-"1000"}
export NITERS=${NITERS:='1'}

for qps in ${MQPS}; do
    for i in `seq 0 1 $NITERS`; do
	## start power logging
	ssh ${TBENCH_SERVER} sudo systemctl stop rapl_log
	ssh ${TBENCH_SERVER} sudo rm /data/rapl_log.log
	ssh ${TBENCH_SERVER} sudo systemctl restart rapl_log

	python img-dnn.py --qps ${qps}

	## stop power logging
	ssh ${TBENCH_SERVER} sudo systemctl stop rapl_log
	#ssh ${TBENCH_SERVER} cat /data/rapl_log.log

	## retrieve logs
	scp -r ${TBENCH_SERVER}:/data/rapl_log.log server_rapl_log.log
	python ~/bayop/tailbench/utilities/parselats.py lats.bin
	rm lats.txt
	rm lats.bin 
	tail -n 10 server_rapl_log.log
	echo "###################################"
    done
done
