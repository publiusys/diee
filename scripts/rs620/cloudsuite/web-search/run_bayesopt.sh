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
		
		rsync --mkpath -avz ${newdir}/* don:/home/handong/cloudlab/rs620/cloudsuite/web_search/linux_static/${newdir}/
	    done
	done
    done
}

function runMult() {
    NTRIALS=40 MQPS=800 PERCENTILE=99 LATENCY=200000 run
    NTRIALS=40 MQPS=400 PERCENTILE=99 LATENCY=200000 run

    NTRIALS=40 MQPS=800 PERCENTILE=90 LATENCY=100000 run
    NTRIALS=40 MQPS=400 PERCENTILE=90 LATENCY=100000 run
}

$@
