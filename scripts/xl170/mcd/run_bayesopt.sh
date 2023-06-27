#!/bin/bash
set -x

export NTRIALS=${NTRIALS:-"1"}
export PERCENTILE=${PERCENTILE:-"99"}
export LATENCY=${LATENCY:-"500"}
export MQPS=${MQPS:-"100000"}

mkdir bayesopt_trials${NTRIALS}_qps${MQPS}_percentile${PERCENTILE}_latency${LATENCY}
time python -u bayesopt.py --trials ${NTRIALS} --qps ${MQPS} --percentile ${PERCENTILE} --latency ${LATENCY} > bayesopt_trials${NTRIALS}_qps${MQPS}_percentile${PERCENTILE}_latency${LATENCY}.log
mv *.out bayesopt_trials${NTRIALS}_qps${MQPS}_percentile${PERCENTILE}_latency${LATENCY}/
mv *.log bayesopt_trials${NTRIALS}_qps${MQPS}_percentile${PERCENTILE}_latency${LATENCY}/

rsync --mkpath -avz bayesopt_trials${NTRIALS}_qps${MQPS}_percentile${PERCENTILE}_latency${LATENCY}/* don:/home/handong/cloudlab/xl170/mcd/linux_static/bayesopt_trials${NTRIALS}_qps${MQPS}_percentile${PERCENTILE}_latency${LATENCY}/
