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
TBENCH_WARMUPREQS = 5000
TBENCH_MAXREQS = 20000
TBENCH_NCLIENTS = 1
TBENCH_CLIENT_THREADS = 1
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

    frames = int(int(GITR)/2)
    #p1 = runRemoteCommand(f"ethtool -C ens1f1np1 rx-frames {GITR} tx-frames {GITR} rx-usecs {GITR} tx-usecs {GITR}", TBENCH_SERVER)
    p1 = runRemoteCommand(f"ethtool -C ens1f1np1 rx-frames {frames} tx-frames {frames} rx-usecs {GITR} tx-usecs {GITR}", TBENCH_SERVER)
    p1.communicate()

def setDVFS():
    global GDVFS
    s = "0x10000"+GDVFS
    p1 = runRemoteCommand(f"wrmsr -a 0x199 {s}", TBENCH_SERVER)
    p1.communicate()
    
def run():
    global TBENCH_QPS
    global TBENCH_WARMUPREQS
    global TBENCH_MAXREQS
    global TBENCH_NCLIENTS
    global TBENCH_SERVER

    ## ensure previous is killed
    killOut = runRemoteCommand(f"pkill -f xapian_networked_server", TBENCH_SERVER)
    killOut.communicate()
    time.sleep(1)

    #LD_LIBRARY_PATH=~/bayop/tailbench/xapian/xapian-core-1.2.13/install/lib TBENCH_NCLIENTS=2 TBENCH_WARMUPREQS=1000 TBENCH_MAXREQS=20000 ./xapian_networked_server -n 10 -d /data/tailbench.inputs/xapian/wiki -r 1000000000
    serverOut = runRemoteCommand(f"LD_LIBRARY_PATH=~/bayop/tailbench/xapian/xapian-core-1.2.13/install/lib TBENCH_SERVER_PORT=8080 TBENCH_SERVER={TBENCH_SERVER} TBENCH_WARMUPREQS={TBENCH_WARMUPREQS} TBENCH_MAXREQS={TBENCH_MAXREQS} TBENCH_NCLIENTS={TBENCH_NCLIENTS} ~/bayop/tailbench/xapian/xapian_networked_server -n 10 -d /data/tailbench.inputs/xapian/wiki -r 1000000000", TBENCH_SERVER)
    time.sleep(5)

    #TBENCH_CLIENT_THREADS=10 TBENCH_SERVER_PORT=8080 TBENCH_SERVER=192.168.1.20 TBENCH_QPS=1000 TBENCH_MINSLEEPNS=100000 TBENCH_TERMS_FILE=/data/tailbench.inputs/xapian/terms.in ./xapian_networked_client
    clientOut1 = runRemoteCommand(f"TBENCH_CLIENT_THREADS={TBENCH_CLIENT_THREADS} TBENCH_SERVER_PORT=8080 TBENCH_SERVER={TBENCH_SERVER} TBENCH_QPS={TBENCH_QPS} TBENCH_MINSLEEPNS=100000 TBENCH_TERMS_FILE=/data/tailbench.inputs/xapian/terms.in ~/bayop/tailbench/xapian/xapian_networked_client", "192.168.1.1")
    clientOut2 = runRemoteCommand(f"TBENCH_CLIENT_THREADS={TBENCH_CLIENT_THREADS} TBENCH_SERVER_PORT=8080 TBENCH_SERVER={TBENCH_SERVER} TBENCH_QPS={TBENCH_QPS} TBENCH_MINSLEEPNS=100000 TBENCH_TERMS_FILE=/data/tailbench.inputs/xapian/terms.in ~/bayop/tailbench/xapian/xapian_networked_client", "192.168.1.2")
    clientOut3 = runRemoteCommand(f"TBENCH_CLIENT_THREADS={TBENCH_CLIENT_THREADS} TBENCH_SERVER_PORT=8080 TBENCH_SERVER={TBENCH_SERVER} TBENCH_QPS={TBENCH_QPS} TBENCH_MINSLEEPNS=100000 TBENCH_TERMS_FILE=/data/tailbench.inputs/xapian/terms.in ~/bayop/tailbench/xapian/xapian_networked_client", "192.168.1.3")

    print("Server Output:")
    for out in serverOut.communicate():
        print(str(out.strip()), end=" ")
    print("")
    
    print("Client1 Output:")
    for out in clientOut1.communicate():
        print(str(out.strip()), end=" ")
    print("")

    print("Client2 Output:")
    for out in clientOut1.communicate():
        print(str(out.strip()), end=" ")
    print("")

    print("Client3 Output:")
    for out in clientOut1.communicate():
        print(str(out.strip()), end=" ")
    print("")
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--qps", help="QPS")
    parser.add_argument("--warmup", help="Warmup requests")
    parser.add_argument("--maxq", help="Max requests")
    parser.add_argument("--nclients", help="Number of clients")
    parser.add_argument("--itr", help="2, 4, etc")
    parser.add_argument("--dvfs", help="0c00 ... 1800")
    

    args = parser.parse_args()
    numTrials = 30
    if args.qps:
        TBENCH_QPS = int(args.qps)
    if args.warmup:
        TBENCH_WARMUPREQS = int(args.warmup)
    if args.maxq:
        TBENCH_MAXREQS = int(args.maxq)
    if args.nclients:
        TBENCH_NCLIENTS = int(args.nclients)
    if args.itr:
        GITR = args.itr
        setITR()
    if args.dvfs:
        GDVFS = args.dvfs
        setDVFS()
        
    print(f"TBENCH_WARMUPREQS={TBENCH_WARMUPREQS} TBENCH_MAXREQS={TBENCH_MAXREQS} TBENCH_NCLIENTS={TBENCH_NCLIENTS} TBENCH_QPS={TBENCH_QPS} TBENCH_SERVER={TBENCH_SERVER} GITR={GITR} GDVFS={GDVFS}")
    
    run()
