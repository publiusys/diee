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

TBENCH_SERVER = "192.168.1.20"
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

def setITR():
    global GITR
    p1 = runRemoteCommand(f"ethtool -C enp3s0f0 rx-usecs {GITR}", TBENCH_SERVER)
    p1.communicate()

def setDVFS():
    global GDVFS
    s = "0x10000"+GDVFS
    p1 = runRemoteCommand(f"wrmsr -a 0x199 {s}", TBENCH_SERVER)
    p1.communicate()

def run():
    global TARGET_QPS
    
    runRemoteCommandGet("pkill -f mutilate", "192.168.1.1")
    runRemoteCommandGet("pkill -f mutilate", "192.168.1.2")
    runRemoteCommandGet("pkill -f mutilate", "192.168.1.3")
    runRemoteCommandGet("pkill -f mutilate", "192.168.1.4")
    time.sleep(1)
    
    runRemoteCommands("~/mutilate/mutilate --agentmode --threads=16", "192.168.1.2")
    runRemoteCommands("~/mutilate/mutilate --agentmode --threads=16", "192.168.1.3")
    runRemoteCommands("~/mutilate/mutilate --agentmode --threads=16", "192.168.1.4")
    time.sleep(1)
    print("pkill mutilate done")
    
    ## rerun mcd
    is_running_mcd = runRemoteCommandGet("pgrep -f memcached", TBENCH_SERVER)
    time.sleep(1)
    if not is_running_mcd:
        print(f"rerunning mcd taskset -c 0-15 ~/memcached/memcached -u nobody -t 16 -m 32G -c 8192 -b 8192 -l {TBENCH_SERVER} -B binary")
        runRemoteCommands(f"taskset -c 0-15 ~/memcached/memcached -u nobody -t 16 -m 32G -c 8192 -b 8192 -l {TBENCH_SERVER} -B binary", TBENCH_SERVER)
        time.sleep(1)
        runRemoteCommands(f"taskset -c 0 ~/mutilate/mutilate --binary -s {TBENCH_SERVER} --loadonly -K fb_key -V fb_value", "192.168.1.1")
        time.sleep(1)

    ## run mutilate
    serverOut = runRemoteCommand(f"taskset -c 0 ~/mutilate/mutilate --binary -s {TBENCH_SERVER} --noload --agent=192.168.1.2,192.168.1.3,192.168.1.4 --threads=1 --keysize=fb_key --valuesize=fb_value --iadist=fb_ia --update=0.25 --depth=4 --measure_depth=1 --connections=16 --measure_connections=32 --measure_qps=2000 --qps={TARGET_QPS} --time=30", "192.168.1.1")

    print("Server Output:")
    f = open(f"mutilate.out", "w")
    for out in serverOut.communicate():
        for line in str(out).strip().split("\\n"):
            f.write(line.strip()+"\n")
    f.close()

    runRemoteCommandGet("pkill -f mutilate", "192.168.1.1")
    runRemoteCommandGet("pkill -f mutilate", "192.168.1.2")
    runRemoteCommandGet("pkill -f mutilate", "192.168.1.3")
    runRemoteCommandGet("pkill -f mutilate", "192.168.1.4")
    time.sleep(1)
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--qps", help="QPS")
    parser.add_argument("--itr", help="2, 4, etc")
    parser.add_argument("--dvfs", help="0c00 ... 1800")    

    args = parser.parse_args()
    if args.qps:
        TARGET_QPS = int(args.qps)
    if args.itr:
        GITR = args.itr
        setITR()
    if args.dvfs:
        GDVFS = args.dvfs
        setDVFS()
        
    print(f"TARGET_QPS={TARGET_QPS} TBENCH_SERVER={TBENCH_SERVER} GITR={GITR} GDVFS={GDVFS}")
    
    run()
