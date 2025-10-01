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
import os.path
from threading import Event, Thread
from statistics import mean

from ax.plot.contour import plot_contour
from ax.plot.trace import optimization_trace_single_method
from ax.utils.notebook.plotting import render, init_notebook_plotting
from ax.service.managed_loop import optimize
from ax.metrics.branin import branin
from ax.utils.measurement.synthetic_functions import hartmann6

import xml.etree.ElementTree as ET

lat_target = 500.0
percentile_target = "99"
TARGET_QPS=100000
TIME = 10
MINLATENCY = False
TBENCH_SERVER = "192.168.1.20"

LATENCIES1 = {
    "50" : 0.0,
    "75" : 0.0,
    "90" : 0.0,
    "95" : 0.0,
    "99" : 0.0,
    "999" : 0.0
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
    print(com, server)
    p1 = Popen(["ssh", server, com], stdout=PIPE, stderr=PIPE)
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

def runWebServer(itr, dvfs):
    print(f"MITR={itr} MDVFS={dvfs} MQPS={TARGET_QPS} ./run_web-server.sh runOneStatic")
    p1 = runLocalCommand(f"MITR={itr} MDVFS={dvfs} MQPS={TARGET_QPS} ./run_web-server.sh runOneStatic")
    for out in p1.communicate():
        for line in str(out).split("\\n"):
            print(line.strip())
            
    name=f"qps{TARGET_QPS}_itr{itr}_dvfs{dvfs}"
    server_rapl = f"server_rapl_{name}.log"
    client1lats = f"client1lats_{name}.txt"
    print(name, server_rapl, client1lats)

    if os.path.isfile(server_rapl) and os.path.isfile(client1lats):
        with open(server_rapl) as file:
            server_rapl_log = [float(line.rstrip()) for line in file]
            joules = 0.0
        if len(server_rapl_log) > 30:
            print("server_rapl_log[20:50]: ", server_rapl_log[20:50])
            print("avg_watts ", mean(server_rapl_log[20:50]))
            joules = mean(server_rapl_log[20:50])
        else:
            # faulty run
            joules = 9999999.0        

        s95 = []
        s99 = []
        s999 = []
        
        with open(client1lats) as file:
            for line in file:
                ## convert to microsecond
                if 'nth="95"' in line.rstrip():
                    tmp = line.rstrip().split('>')[1].split('<')[0]
                    if tmp.isnumeric():
                        s95.append(float(tmp)*1000.0)
                    else:
                        s95.append(9999.0*1000.0)
                if 'nth="99"' in line.rstrip():
                    tmp = line.rstrip().split('>')[1].split('<')[0]
                    if tmp.isnumeric():
                        s99.append(float(tmp)*1000.0)
                    else:
                        s99.append(9999.0*1000.0)
                if 'nth="99.9"' in line.rstrip():
                    tmp = line.rstrip().split('>')[1].split('<')[0]
                    if tmp.isnumeric():
                        s999.append(float(tmp)*1000.0)
                    else:
                        s999.append(9999.0*1000.0)
                    
        LATENCIES1["95"] = max(s95)
        LATENCIES1["99"] = max(s99)
        LATENCIES1["999"] = max(s999)
        print(LATENCIES1)
        return joules, LATENCIES1[percentile_target]
    else:
        return -1.0, -1.0
    

def web_server_eval_func(params):
    global lat_target
    global percentile_target
    global TARGET_QPS

    # launch experiment with params
    itr = str(int(params['itr']))
    dvfs = int2hexstr(int(params['dvfs']))
    print(itr, dvfs)

    joules, meanlatency = runWebServer(itr, dvfs)
    if joules == -1.0:
        sys.exit("joules == -1.0")
        
    old_joules = joules
    ## if ITR, DVFS results in SLA violation then bump up energy use
    if meanlatency > lat_target:
        joules = joules * (meanlatency-lat_target+1)

    print(f"{percentile_target}% <= {lat_target} us: ITR={itr} DVFS={dvfs} Energy={joules} ({old_joules}) Latency={meanlatency}")
    print("")
    
    res = {
        'web_server': (joules, 0.0)
    }
    return res

def perform_bayesopt(metric = 'read_99th_mean', minimize = True, ntrials=30):
    global MINLATENCY
    
    results = {}
    counter = 0
    
    itr_vals = [*range(2, 1000, 2)]
    dvfs_vals = [*range(3072, 5632, 1)]
    
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
                                                   evaluation_function=lambda params: web_server_eval_func(params),
                                                   experiment_name=f'web_server_discrete',
                                                   objective_name='web_server',
                                                   minimize=minimize,
                                                   total_trials=ntrials)
    else:
        best_params, values, exp, model = optimize(parameters=search_space,
                                                   evaluation_function=lambda params: web_server_eval_func(params),
                                                   experiment_name=f'web_server_discrete',
                                                   objective_name='web_server',
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
