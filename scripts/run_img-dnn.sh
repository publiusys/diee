#! /bin/bash

currdate=`date +%m_%d_%Y_%H_%M_%S`
set -x

## start power logging
ssh ${TBENCH_SERVER} sudo systemctl stop rapl_log
ssh ${TBENCH_SERVER} sudo rm /data/rapl_log.log
ssh ${TBENCH_SERVER} sudo systemctl restart rapl_log

python img-dnn.py

## stop power logging
ssh ${TBENCH_SERVER} sudo systemctl stop rapl_log
#ssh ${TBENCH_SERVER} cat /data/rapl_log.log

## retrieve logs
scp -r ${TBENCH_SERVER}:/data/rapl_log.log server_rapl_log.log
python ~/bayop/tailbench/utilities/parselats.py lats.bin
rm lats.txt
rm lats.bin 
tail -n 10 server_rapl_log.log
