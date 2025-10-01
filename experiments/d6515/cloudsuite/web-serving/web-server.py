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
TBENCH_QPS = 1000
TBENCH_NCORES = 1
GITR = ""
GDVFS = ""

def runRemoteCommand(com, server):
    print("ssh", server, com)    
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
    print(com)
    p1 = Popen(com, shell=True, stdout=PIPE, stderr=PIPE)
    #p1 = Popen(list(filter(None, com.strip().split(' '))), stdout=PIPE, stderr=PIPE)
    return p1

def setITR():
    global GITR

    ieth = runRemoteCommandGet("ifconfig | grep -B1 192.168.1 | grep -o '^\w*'", TBENCH_SERVER).decode()
    frames = int(int(GITR)/2)
    p1 = runRemoteCommand(f"ethtool -C {ieth} rx-frames {frames} tx-frames {frames} rx-usecs {GITR} tx-usecs {GITR}", TBENCH_SERVER)
    p1.communicate()

def setDVFS():
    global GDVFS

    #0x0 = 2.35GHz
    #0x1 = 2.00GHz
    #0x2 = 1.50GHz
    
    p1 = runRemoteCommand(f"wrmsr -a 0xc0010062 {GDVFS}", TBENCH_SERVER)
    p1.communicate()
    
def run():
    global TBENCH_QPS
    global TBENCH_SERVER
    global TBENCH_NCORES
    
    clientOut1 = runRemoteCommand(f"docker exec faban_client run/entrypoint.sh {TBENCH_SERVER} {TBENCH_QPS}", "192.168.1.1")
    
    print("Client1 Output:")
    f = open("clientOut.log", "w")
    for out in clientOut1.communicate():
        for line in str(out).strip().split("\\n"):
            f.write(line+"\n")
    print("")
    f.close()
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--qps", help="QPS")
    parser.add_argument("--itr", help="2, 4, etc")
    parser.add_argument("--dvfs", help="0c00 ... 1800")
    
    args = parser.parse_args()
    numTrials = 30
    if args.qps:
        TBENCH_QPS = int(args.qps)
    if args.itr:
        GITR = args.itr
        setITR()
    if args.dvfs:
        GDVFS = args.dvfs
        setDVFS()

    TBENCH_NCORES = int(runLocalCommandOut("nproc"))
    
    print(f"TBENCH_NCORES={TBENCH_NCORES} TBENCH_QPS={TBENCH_QPS} TBENCH_SERVER={TBENCH_SERVER} GITR={GITR} GDVFS={GDVFS}")
    run()
