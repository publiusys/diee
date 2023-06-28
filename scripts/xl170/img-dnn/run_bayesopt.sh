#!/bin/bash
set -x

export NTRIALS=${NTRIALS:-"1"}
export PERCENTILE=${PERCENTILE:-"99"}
export LATENCY=${LATENCY:-"5000"}
export MQPS=${MQPS:-"1000"}

newdir="bayesopt_trials${NTRIALS}_qps${MQPS}_percentile${PERCENTILE}_latency${LATENCY}" 
mkdir ${newdir}
time python -u bayesopt.py --trials ${NTRIALS} --qps ${MQPS} --percentile ${PERCENTILE} --latency ${LATENCY} > ${newdir}/"${newdir}.log"
mv *.bin ${newdir}
mv *.log ${newdir}
mv *.txt ${newdir}

rsync --mkpath -avz ${newdir}/* don:/home/handong/cloudlab/xl170/img-dnn/linux_static/${newdir}/
