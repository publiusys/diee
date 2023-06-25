#!/bin/bash
set -x

export NTRIALS=${NTRIALS:-"60"}

#qps=2000
#
#mkdir bayesopt_trials${NTRIALS}_qps${qps}_percentile${percentile}_latency5000
#time python -u bayesopt.py --trials ${NTRIALS} --qps ${qps} --percentile ${percentile} --latency 5000 > bayesopt_trials${NTRIALS}_qps${qps}_percentile${percentile}_latency5000.log
#mv *qps*.* bayesopt_trials${NTRIALS}_qps${qps}_percentile${percentile}_latency5000

percentile=99
qps=1500
mkdir bayesopt_trials${NTRIALS}_qps${qps}_percentile${percentile}_latency5000
time python -u bayesopt.py --trials ${NTRIALS} --qps ${qps} --percentile ${percentile} --latency 5000 > bayesopt_trials${NTRIALS}_qps${qps}_percentile${percentile}_latency5000.log
mv *qps*.* bayesopt_trials${NTRIALS}_qps${qps}_percentile${percentile}_latency5000

qps=2500
mkdir bayesopt_trials${NTRIALS}_qps${qps}_percentile${percentile}_latency5000
time python -u bayesopt.py --trials ${NTRIALS} --qps ${qps} --percentile ${percentile} --latency 5000 > bayesopt_trials${NTRIALS}_qps${qps}_percentile${percentile}_latency5000.log
mv *qps*.* bayesopt_trials${NTRIALS}_qps${qps}_percentile${percentile}_latency5000

qps=3000
mkdir bayesopt_trials${NTRIALS}_qps${qps}_percentile${percentile}_latency5000
time python -u bayesopt.py --trials ${NTRIALS} --qps ${qps} --percentile ${percentile} --latency 5000 > bayesopt_trials${NTRIALS}_qps${qps}_percentile${percentile}_latency5000.log
mv *qps*.* bayesopt_trials${NTRIALS}_qps${qps}_percentile${percentile}_latency5000

echo "**************************************************************"
qps=1000
percentile=90
mkdir bayesopt_trials${NTRIALS}_qps${qps}_percentile${percentile}_latency5000
time python -u bayesopt.py --trials ${NTRIALS} --qps ${qps} --percentile ${percentile} --latency 5000 > bayesopt_trials${NTRIALS}_qps${qps}_percentile${percentile}_latency5000.log
mv *qps*.* bayesopt_trials${NTRIALS}_qps${qps}_percentile${percentile}_latency5000

qps=1500
mkdir bayesopt_trials${NTRIALS}_qps${qps}_percentile${percentile}_latency5000
time python -u bayesopt.py --trials ${NTRIALS} --qps ${qps} --percentile ${percentile} --latency 5000 > bayesopt_trials${NTRIALS}_qps${qps}_percentile${percentile}_latency5000.log
mv *qps*.* bayesopt_trials${NTRIALS}_qps${qps}_percentile${percentile}_latency5000

qps=2000
mkdir bayesopt_trials${NTRIALS}_qps${qps}_percentile${percentile}_latency5000
time python -u bayesopt.py --trials ${NTRIALS} --qps ${qps} --percentile ${percentile} --latency 5000 > bayesopt_trials${NTRIALS}_qps${qps}_percentile${percentile}_latency5000.log
mv *qps*.* bayesopt_trials${NTRIALS}_qps${qps}_percentile${percentile}_latency5000

qps=2500
mkdir bayesopt_trials${NTRIALS}_qps${qps}_percentile${percentile}_latency5000
time python -u bayesopt.py --trials ${NTRIALS} --qps ${qps} --percentile ${percentile} --latency 5000 > bayesopt_trials${NTRIALS}_qps${qps}_percentile${percentile}_latency5000.log
mv *qps*.* bayesopt_trials${NTRIALS}_qps${qps}_percentile${percentile}_latency5000

qps=3000
mkdir bayesopt_trials${NTRIALS}_qps${qps}_percentile${percentile}_latency5000
time python -u bayesopt.py --trials ${NTRIALS} --qps ${qps} --percentile ${percentile} --latency 5000 > bayesopt_trials${NTRIALS}_qps${qps}_percentile${percentile}_latency5000.log
mv *qps*.* bayesopt_trials${NTRIALS}_qps${qps}_percentile${percentile}_latency5000

