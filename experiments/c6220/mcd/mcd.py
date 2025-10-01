import math
import random
import subprocess
from subprocess import Popen, PIPE, call
import time
from datetime import datetime
import sys
import getopt
import os
import numpy as np
import itertools
import argparse
import shutil

TBENCH_SERVER = ""
TBENCH_AGENTS = []
TARGET_QPS = 50000
GITR = ""
GDVFS = ""
#GITR = "2"
#GDVFS = "0c00"

def runRemoteCommand(com, server):
    print("ssh", server, com)    
    p1 = Popen(["ssh", server, com], stdout=PIPE, stderr=PIPE)
    return p1

def runRemoteCommandGet(com, server):
    p1 = Popen(["ssh", server, com], stdout=PIPE, stderr=PIPE)
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
    print(com)
    p1 = Popen(com, shell=True, stdout=PIPE, stderr=PIPE)
    #p1 = Popen(list(filter(None, com.strip().split(' '))), stdout=PIPE, stderr=PIPE)
    return p1

def cleanITRlogs():
    global TBENCH_SERVER
    p1 = runRemoteCommand(f"cat /proc/ixgbe_stats/core/*", TBENCH_SERVER)
    p1.communicate()

def getITRlogs():
    global TBENCH_SERVER
    for i in range(16):
        p1 = runRemoteCommand(f"cat /proc/ixgbe_stats/core/{i} > ~/mcd.log.{i}", TBENCH_SERVER)
        p1.communicate()
    
def setITR():
    global GITR
    global TBENCH_SERVER

    print(TBENCH_SERVER)
    
    print(" -------------------- setITR on victim --------------------")
    ieth = runRemoteCommandGet("ifconfig | grep -B1 10.10.1 | grep -o '^\w*'", TBENCH_SERVER).decode()
    p1 = runRemoteCommand(f"ethtool -C {ieth} rx-usecs {GITR}", TBENCH_SERVER)
    p1.communicate()

    p1 = runRemoteCommand(f"ethtool -c {ieth} | grep usecs", TBENCH_SERVER)
    print(p1.communicate()[0].strip().decode())
    print("")
    
def setDVFS():
    global GDVFS
    global TBENCH_SERVER

    #p1 = runRemoteCommand(f"~/experiment-scripts/cloudlab_setup/c6220/set_dvfs.sh userspace", TBENCH_SERVER)
    #p1.communicate()
    
    print(" -------------------- setDVFS on victim --------------------")
    s = "0x10000"+GDVFS
    p1 = runRemoteCommand(f"wrmsr -a 0x199 {s}", TBENCH_SERVER)
    p1.communicate()
    
    time.sleep(0.5)
    # print CPU frequency across all cores
    p1 = runRemoteCommand(f"rdmsr -a 0x199", TBENCH_SERVER)
    print(p1.communicate()[0].strip().decode())
    print("")

def run():
    global TARGET_QPS
    global TBENCH_SERVER
    global TBENCH_AGENTS

    for agent in TBENCH_AGENTS:        
        runRemoteCommandGet("pkill -f mutilate", agent)
    time.sleep(1)

    for agent in TBENCH_AGENTS[1:]:
        runRemoteCommands("~/mutilate/mutilate --agentmode --threads=16", agent)
    time.sleep(1)
    print("pkill mutilate done")
    
    ## rerun mcd
    is_running_mcd = runRemoteCommandGet("pgrep -f memcached", TBENCH_SERVER)
    time.sleep(1)
    if not is_running_mcd:
        print(f"rerunning mcd taskset -c 0-15 ~/memcached/memcached -u nobody -t 16 -m 32G -c 8192 -b 8192 -l {TBENCH_SERVER} -B binary")
        runRemoteCommands(f"taskset -c 0-15 ~/memcached/memcached -u nobody -t 16 -m 32G -c 8192 -b 8192 -l {TBENCH_SERVER} -B binary", TBENCH_SERVER)
        time.sleep(1)
        runRemoteCommands(f"taskset -c 0 ~/mutilate/mutilate --binary -s {TBENCH_SERVER} --loadonly -K fb_key -V fb_value", TBENCH_AGENTS[0])
        time.sleep(1)

    cleanITRlogs()
    ## run mutilate    
    serverOut = runRemoteCommand(f"taskset -c 0 ~/mutilate/mutilate --binary -s {TBENCH_SERVER} --noload --agent={','.join(TBENCH_AGENTS[1:])} --threads=1 --keysize=fb_key --valuesize=fb_value --iadist=fb_ia --update=0.25 --depth=4 --measure_depth=1 --connections=16 --measure_connections=32 --measure_qps=2000 --qps={TARGET_QPS} --time=30", TBENCH_AGENTS[0])        
    
    print("Server Output:")
    f = open(f"mutilate.out", "w")
    for out in serverOut.communicate():
        for line in str(out).strip().split("\\n"):
            f.write(line.strip()+"\n")
    f.close()
    
    getITRlogs()

    for agent in TBENCH_AGENTS:        
        runRemoteCommandGet("pkill -f mutilate", agent)
    time.sleep(1)        
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--qps", help="QPS")
    parser.add_argument("--itr", help="2, 4, etc")
    parser.add_argument("--dvfs", help="0c00 ... 1800")    
    parser.add_argument("--server", help="single server ip addresses")
    parser.add_argument("--agents", help="comma delimited agent ip addresses")
    
    args = parser.parse_args()
    if args.server:
        TBENCH_SERVER = args.server
    else:
        print(f"Need valid --server: {args.server}")
        exit()
    
    if args.agents:
        TBENCH_AGENTS = (args.agents).strip().split(',')
    else:
        print(f"Need valid --agents: {args.agents}")
        exit()
        
    if args.qps:
        TARGET_QPS = int(args.qps)
    if args.itr:
        GITR = args.itr
        setITR()
    if args.dvfs:
        GDVFS = args.dvfs
        setDVFS()
            
    print(f"TARGET_QPS={TARGET_QPS} TBENCH_SERVER={TBENCH_SERVER} TBENCH_AGENTS={TBENCH_AGENTS} GITR={GITR} GDVFS={GDVFS}")
    
    run()
