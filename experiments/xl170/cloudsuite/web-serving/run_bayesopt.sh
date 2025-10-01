#!/bin/bash
#set -x

export NTRIALS=${NTRIALS:-"60"}
export PERCENTILE=${PERCENTILE:-"90"}
export LATENCY=${LATENCY:-"5000"}
export MQPS=${MQPS:-"1500"}

function run() {
    for qps in ${MQPS}; do
	for percentile in ${PERCENTILE}; do
	    for latency in ${LATENCY}; do
		newdir="bayesopt_trials${NTRIALS}_qps${qps}_percentile${percentile}_latency${latency}"
		echo $newdir
		mkdir ${newdir}
		python -u bayesopt.py --trials ${NTRIALS} --qps ${qps} --percentile ${percentile} --latency ${latency} > ${newdir}/"${newdir}.log"
		mv *.log ${newdir}
		mv *.txt ${newdir}
		
		rsync --mkpath -avz ${newdir}/* don:/home/handong/cloudlab/xl170/cloudsuite/web_server/linux_static/${newdir}/
	    done
	done
    done
}

function runMult() {
    ## 99.9% < 2000 ms
    NTRIALS=40 MQPS=5 PERCENTILE=999 LATENCY=2000000 run
    NTRIALS=40 MQPS=10 PERCENTILE=999 LATENCY=2000000 run
    NTRIALS=40 MQPS=20 PERCENTILE=999 LATENCY=2000000 run

    ## 95% < 500 ms
    NTRIALS=40 MQPS=5 PERCENTILE=95 LATENCY=500000 run
    NTRIALS=40 MQPS=10 PERCENTILE=95 LATENCY=500000 run
    NTRIALS=40 MQPS=20 PERCENTILE=95 LATENCY=500000 run
}

$@
