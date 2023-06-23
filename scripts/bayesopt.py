import math
import random
import subprocess
from subprocess import Popen, PIPE, call
import time
from datetime import datetime
import sys
import getopt
import numpy as np
import itertools
import argparse
import shutil

import numpy as np
import itertools
from pprint import pprint
import pandas as pd
import os
from threading import Event, Thread
from statistics import mean

from ax.plot.contour import plot_contour
from ax.plot.trace import optimization_trace_single_method
from ax.utils.notebook.plotting import render, init_notebook_plotting
from ax.service.managed_loop import optimize
from ax.metrics.branin import branin
from ax.utils.measurement.synthetic_functions import hartmann6

condition = Event()
MASTER = "192.168.1.37"
CSERVER = "192.168.1.11"
CSERVER2 = "192.168.1.11"
lat_target = 500.0
percentile_target = "99"
TARGET_QPS=100000
TYPE = 'etc'
TIME = 10
MINLATENCY = False

WORKLOADS = {
    #ETC = 75% GET, 25% SET
    'etc': '--keysize=fb_key --valuesize=fb_value --iadist=fb_ia --update=0.25',
    #USR = 99% GET, 1% SET
    'usr': '--keysize=19 --valuesize=2 --update=0.01',
    'etc2': '--keysize=fb_key --valuesize=fb_value --iadist=fb_ia --update=0.033'
}

LATENCIES = {
    "50" : 0.0,
    "75" : 0.0,
    "90" : 0.0,
    "95" : 0.0,
    "99" : 0.0
}

#print(hex2int("0c00"))
    #print(hex2int("1800"))
    #print(int2hexstr(3072))
    #print(int2hexstr(6144))
    
def hex2int(hex_str):
    return int(hex_str,16)

def int2hexstr(int_in):
    s = str(hex(int_in))
    s2 = s[2:]
    if len(s2) == 3:
        s2 = "0"+s2
    assert len(s2) == 4
    return s2
        
def runRemoteCommand(com, server):
    p1 = Popen(["ssh", server, com], stdout=PIPE)
    return p1

def runRemoteCommandGet(com, server):
    p1 = Popen(["ssh", server, com], stdout=PIPE)
    return p1.communicate()[0].strip()

def runRemoteCommands(com, server):
    Popen(["ssh", server, com])
    
def runLocalCommandOut(com):
    #print(com)
    p1 = Popen(list(filter(None, com.strip().split(' '))), stdout=PIPE)
    return p1.communicate()[0].strip()

def runLocalCommands(com):
    Popen(list(filter(None, com.strip().split(' '))))

def runLocalCommand(com):
    p1 = Popen(com, shell=True, stdout=PIPE, stderr=PIPE)
    return p1

def setITR(v):
    p1 = Popen(["ssh", CSERVER2, "/app/ethtool-4.5/ethtool -C eth0 rx-usecs", v], stdout=PIPE, stderr=PIPE)
    p1.communicate()

def setDVFS(v):
    p1 = Popen(["ssh", CSERVER2, "wrmsr -a 0x199", v], stdout=PIPE, stderr=PIPE)
    p1.communicate()

def getEnergy():
    output = 0.0    
    while True:
        p1 = Popen(["ssh", CSERVER2, "/app/uarch-configure/rapl-read/raplog -c 1"], stdout=PIPE)    
        output = float(p1.communicate()[0].strip().decode('ascii'))

        ## check if a reading is valid as RAPL energy counter can overflow
        ## idles at ~35 Watts, ignore idling numbers inbetween experiments
        if output > 48.0 and output < 5000.0:
            break
        #else:
        #    print("RAPL energy: ", output)
    return output

def startMcd():
    runRemoteCommands("taskset -c 0 /app/memcached/memcached -u nobody -t 1 -m 2G -c 8192 -b 8192 -l 192.168.1.11 -B binary -p 11212", "192.168.1.11")
    time.sleep(1)

def checkMemcached():
    run = True
    ## check if memcached is running
    while run:
        p1 = Popen(["ssh", "192.168.1.11", "pgrep memcached"], stdout=PIPE)
        isRun1 = p1.communicate()[0].strip()        
        if isRun1:
            run = False
            break
        else:
            print("Starting memcached")
            startMcd()
            #time.sleep(1)
            
def getLatency():
    global lat_target
    global percentile_target
    
    checkMemcached()
    #output = runLocalCommandOut("taskset -c 0-15 /root/github/mutilate/mutilate --binary -s 192.168.1.11:11212 --noload --threads=16 --keysize=fb_key --valuesize=fb_value --update=0.25 --iadist=fb_ia --depth=1 --measure_depth=1 --connections=16 --measure_connections=16 --measure_qps=2000 --qps=10000 --time 1")
    output = runLocalCommandOut("/root/github/mutilate/mutilate --binary -s 192.168.1.11:11212 --noload --threads=14 --keysize=fb_key --valuesize=fb_value --update=0.25 --iadist=fb_ia --depth=1 --measure_depth=1 --connections=14 --measure_connections=14 --measure_qps=2000 --qps=50000 --time 5")
    
    r5th = 0
    r10th = 0
    r50th = 0
    r90th = 0
    r95th = 0
    r99th = 0
    for line in str(output).strip().split("\\n"):
        if "read" in line:
            alla = list(filter(None, line.strip().split(' ')))
            r5th = float(alla[4])
            r10th = float(alla[5])
            r50th = float(alla[6])
            r90th = float(alla[7])
            r95th = float(alla[8])
            r99th = float(alla[9])
    print(f"5%={r5th}, 10%={r10th}, 50%={r50th}, 90%={r90th}, 95%={r95th}, 99%={r99th}")
    if percentile_target == 5:
        return r5th
    elif percentile_target == 10:
        return r10th
    elif percentile_target == 50:
        return r50th
    elif percentile_target == 90:
        return r90th
    elif percentile_target == 95:
        return r95th
    elif percentile_target == 99:
        return r99th
    else:
        print(f"percentile_target == {percentile_target} not valid")
        exit()

    
    #return r5th, r10th, r50th, r90th, r95th, r99th
    #p1 = Popen(["ssh", "192.168.1.37", "tail -n 1 ~/tlog.log"], stdout=PIPE)    
    #output = p1.communicate()[0].strip().decode('ascii').split(' ')
    #avg = float(output[0])
    #stddev = float(output[1])
    #r10th = float(output[2])
    #r50th = float(output[3])
    #r90th = float(output[4])
    #r95th = float(output[5])
    #r99th = float(output[6])
    #print(avg, stddev, r10th, r50th, r90th, r95th, r99th)
    #return r99th

def checkMutilate():
    ## check if mutilate is running
    while True:
        p1 = Popen(["ssh", "192.168.1.37", "pgrep mutilate"], stdout=PIPE)
        p2 = Popen(["ssh", "192.168.1.38", "pgrep mutilate"], stdout=PIPE)
        p3 = Popen(["ssh", "192.168.1.104", "pgrep mutilate"], stdout=PIPE)
        isRun1 = p1.communicate()[0].strip()
        isRun2 = p2.communicate()[0].strip()
        isRun3 = p3.communicate()[0].strip()
        
        if isRun1 and isRun2 and isRun3:
            break
        else:
            print("Waiting for mutilate to start")
            time.sleep(1)

def runMcd():
    global lat_target
    global percentile_target
    global TARGET_QPS
    global TIME
    global TYPE
    
    ##    
    #print("Run Mutilate", TYPE, TARGET_QPS, TIME)        
    runRemoteCommandGet("pkill mutilate", "192.168.1.38")
    runRemoteCommandGet("pkill mutilate", "192.168.1.104")
    runRemoteCommandGet("pkill mutilate", "192.168.1.37")
    time.sleep(1)    
    runRemoteCommands("/app/mutilate/mutilate --agentmode --threads=16", "192.168.1.38")
    runRemoteCommands("/app/mutilate/mutilate --agentmode --threads=16", "192.168.1.104")
    time.sleep(1)
    #print("pkill done")
        
    ## rerun mcd
    is_running_mcd = runRemoteCommandGet("pgrep memcached", "192.168.1.11")
    time.sleep(1)
    if is_running_mcd:
        bad=0
    else:
        runRemoteCommands("taskset -c 0-15 /app/memcached/memcached -u nobody -t 16 -m 32G -c 8192 -b 8192 -l 192.168.1.11 -B binary", "192.168.1.11")
        time.sleep(1)
        runRemoteCommands("taskset -c 0 /app/mutilate/mutilate --binary -s 192.168.1.11 --loadonly -K fb_key -V fb_value", "192.168.1.37")
        time.sleep(1)
        
    ## run mutilate
    p1 = runRemoteCommand("taskset -c 0-15 /app/mutilate/mutilate --binary -s 192.168.1.11 --noload --agent=192.168.1.38,192.168.1.104 --threads=16 "+WORKLOADS[TYPE]+" --depth=4 --measure_depth=1 --connections=16 --measure_connections=32 --measure_qps=2000 --qps="+str(TARGET_QPS)+" --time="+str(TIME), "192.168.1.37")
    #print("start mutilate")
    p2 = runLocalCommand("/root/asplos23/rapl_log.sh "+str(TIME))
    #print("start rapl")
    output = p1.communicate()[0].strip()    
    runRemoteCommands("killall -USR2 memcached", "192.168.1.11")
    
    for line in str(output).strip().split("\\n"):
        if "read" in line:
            alla = list(filter(None, line.strip().split(' ')))
            #print(alla)
            r5th = float(alla[4])
            r10th = float(alla[5])
            r50th = float(alla[6])
            r90th = float(alla[7])
            r95th = float(alla[8])
            r99th = float(alla[9])
        if "Total QPS" in line:
            alla = list(filter(None, line.strip().split(' ')))
            #print(alla)
            totalQPS = alla[3]

    output = p2.communicate()[0].strip().decode('ascii')
    tmpl = []
    #print(output)
    for line in str(output).split("\n"):
        if float(line) > 40.0 and float(line) < 5000.0:
            tmpl.append(float(line))
    jl = tmpl[2:len(tmpl)-2]
    #print(jl)
    #print(totalQPS, r5th, r10th, r50th, r90th, r95th, r99th)
    if percentile_target == 5:
        rth = r5th
    elif percentile_target == 10:
        rth = r10th
    elif percentile_target == 50:
        rth = r50th
    elif percentile_target == 90:
        rth = r90th
    elif percentile_target == 95:
        rth = r95th
    elif percentile_target == 99:
        rth = r99th
    else:
        print(f"percentile_target == {percentile_target} not valid")
        exit()
    joules = sum(jl)/len(jl)
    return rth, joules
        
## param: ITR, DVFS
def mcd_eval_func2(params):
    global lat_target
    global percentile_target
    global TARGET_QPS
    global TIME
    global TYPE
    
    # launch experiment with params
    itr = str(int(params['itr']))
    #dvfs = str(hex(int(params['dvfs'])))
    dvfs = str(int(params['dvfs']))
    
    ## set ITR, DVFS
    setITR(itr)
    setDVFS(dvfs)
    #print(itr, dvfs)    

    rth, joules = runMcd()
    
    old_joules = joules
    ## if ITR, DVFS results in SLA violation then bump up energy use
    if rth > lat_target:
        #joules += ((r99th/500.0)*joules)
        #print(joules, joules+(10 * (r99th-505.0)), r99th)
        #joules = joules + (10 * (r99th-505.0))
        ## Joules: 35W -> 140W
        joules = joules * (rth-lat_target+1)

    print(f"reward=({percentile_target}% <= {lat_target}us): ITR={itr}, DVFS={dvfs}, Energy={joules} ({old_joules}), Latency={rth}")
    print("")    
        
    res = {
        'mcd': (joules, 0.0)
    }
    return res

def mcd_eval_func_lat(params):
    global lat_target
    global percentile_target
    global TARGET_QPS
    global TIME
    global TYPE
    
    # launch experiment with params
    itr = str(int(params['itr']))
    dvfs = str(int(params['dvfs']))
    
    ## set ITR, DVFS
    setITR(itr)
    setDVFS(dvfs)    
    rth, joules = runMcd()

    print(f"reward=({percentile_target}% <= {lat_target}us): ITR={itr}, DVFS={dvfs}, Energy={joules} ({joules}), Latency={rth}")
    print("")    
        
    res = {
        'mcd': (rth, 0.0)
    }
    return res

def img_dnn_eval_func(params):
    global lat_target
    global percentile_target
    global TARGET_QPS

    # launch experiment with params
    itr = str(int(params['itr']))
    dvfs = int2hexstr(int(params['dvfs']))
    print(itr, dvfs)

    print(f"MITR={itr} MDVFS={dvfs} MQPS={TARGET_QPS} ./run_img-dnn.sh runOne")
    p1 = runLocalCommand(f"MITR={itr} MDVFS={dvfs} MQPS={TARGET_QPS} ./run_img-dnn.sh runOne")
    p1.communicate()
    #for out in p1.communicate():
    #    for line in str(out).split("\\n"):
    #        print(line.strip())    
    name=f"qps{TARGET_QPS}_itr{itr}_dvfs{dvfs}"
    server_rapl = f"server_rapl_{name}.log"
    client1lats = f"client1lats_{name}.txt"
    print(name, server_rapl, client1lats)

    with open(server_rapl) as file:
        server_rapl_log = [float(line.rstrip()) for line in file]
    #assert len(server_rapl_log) > 25

    joules = 0.0
    if len(server_rapl_log) > 25:
        print("server_rapl_log[15:25]: ", server_rapl_log[15:25])
        print("avg_watts ", mean(server_rapl_log[15:25]))
        joules = mean(server_rapl_log[15:25])
    else:
        # faulty run
        joules = 9999999.0

    with open(client1lats) as file:
        for line in file:
            ## convert to microsecond
            if "50th" in line.rstrip():
                LATENCIES["50"] = float((line.rstrip().split(" "))[3]) * 1000.0
            if "75th" in line.rstrip():
                LATENCIES["75"] = float((line.rstrip().split(" "))[3]) * 1000.0
            if "90th" in line.rstrip():
                LATENCIES["90"] = float((line.rstrip().split(" "))[3]) * 1000.0
            if "95th" in line.rstrip():
                LATENCIES["95"] = float((line.rstrip().split(" "))[3]) * 1000.0
            if "99th" in line.rstrip():
                LATENCIES["99"] = float((line.rstrip().split(" "))[3]) * 1000.0

    print(LATENCIES)
    
    old_joules = joules
    ## if ITR, DVFS results in SLA violation then bump up energy use
    if LATENCIES[percentile_target] > lat_target:
        #joules += ((r99th/500.0)*joules)
        #print(joules, joules+(10 * (r99th-505.0)), r99th)
        #joules = joules + (10 * (r99th-505.0))
        ## Joules: 35W -> 140W
        joules = joules * (LATENCIES[percentile_target]-lat_target+1)

    print(f"reward=({percentile_target}% <= {lat_target} us): ITR={itr}, DVFS={dvfs}, Energy={joules} ({old_joules}), Latency={LATENCIES[percentile_target]}")
    print("")
    
    res = {
        'img_dnn': (joules, 0.0)
    }
    return res

def perform_bayesopt(metric = 'read_99th_mean', minimize = True, ntrials=30):
    global MINLATENCY
    
    results = {}
    counter = 0
    
    itr_vals = [*range(2, 1000, 2)]
    dvfs_vals = [*range(3072, 6144, 1)]
    
    search_space = [{'is_ordered': True,
                     'log_scale': False,
                     'name': 'itr',
                     'type': 'choice',
                     'value_type': 'float',
                     'values': itr_vals},
                    {'is_ordered': True,
                     'log_scale': False,
                     'name': 'dvfs',
                     'type': 'choice',
                     'value_type': 'float',
                     'values': dvfs_vals}]

    print(f"search space: ITR={len(itr_vals)} DVFS={len(dvfs_vals)}")
    #pprint(search_space)

    if MINLATENCY == True:        
        best_params, values, exp, model = optimize(parameters=search_space,
                                                   evaluation_function=lambda params: img_dnn_eval_func(params),
                                                   experiment_name=f'img_dnn_discrete',
                                                   objective_name='img_dnn',
                                                   minimize=minimize,
                                                   total_trials=ntrials)
    else:
        best_params, values, exp, model = optimize(parameters=search_space,
                                                   evaluation_function=lambda params: img_dnn_eval_func(params),
                                                   experiment_name=f'img_dnn_discrete',
                                                   objective_name='img_dnn',
                                                   minimize=minimize,
                                                   total_trials=ntrials)
        
    print(f"best_params: itr={str(int(best_params['itr']))} dvfs={int2hexstr(int(best_params['dvfs']))}")
    
    ## set best ITR, DVFS
    #setITR(str(int(best_params['itr'])))
    #setDVFS(str(int(best_params['dvfs'])))
    
if __name__ == '__main__':    
    parser = argparse.ArgumentParser()
    parser.add_argument("--trials", help="Number of trials to run")
    parser.add_argument("--verbose", help="increase output verbosity")
    parser.add_argument("--latency", help="e.g. [200, 250, 350, 450]")
    parser.add_argument("--percentile", help="e.g. [10, 50, 90, 99]")
    parser.add_argument("--qps", required=True, help="Requests-per-second to run bayesopt")
    parser.add_argument("--time", help="time to run")
    parser.add_argument("--minlatency", help="minimize latency")
    
    args = parser.parse_args()
    numTrials = 30
    if args.trials:
        numTrials = int(args.trials)
    if args.latency:
        lat_target = float(int(args.latency))
    if args.percentile:
        percentile_target = args.percentile
    if args.qps:
        TARGET_QPS=int(args.qps)        
    if args.time:
        TIME=int(args.time)
    if args.minlatency:
        MINLATENCY=True
    if args.verbose:
        print(f"numTrials={numTrials}, lat_target={lat_target}, percentile_target={percentile_target}, TARGET_QPS={TARGET_QPS}, TIME={TIME}, MINLATENCY={MINLATENCY}")
            
        
    perform_bayesopt(ntrials=numTrials)
    
    #com="/root/asplos23/rapl_log.sh "+str(TIME)
    #p2 = Popen(list(filter(None, com.strip().split(' '))), stdout=PIPE)
    #output = p2.communicate()[0].strip().decode('ascii')
    #ll = []
    #print(output)
    #for line in str(output).split("\n"):
    #    ll.append(float(line))
    #    print(line)
    #print(ll[1:len(ll)-1])
    #print(p1.communicate()[0].strip().decode('ascii'))
