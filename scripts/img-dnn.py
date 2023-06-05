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

TBENCH_SERVER = os.getenv('TBENCH_SERVER')
TBENCH_QPS = 1000
TBENCH_WARMUPREQS = 5000
TBENCH_MAXREQS = 20000
TBENCH_NCLIENTS = 1

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

def run():
    global TBENCH_QPS
    global TBENCH_WARMUPREQS
    global TBENCH_MAXREQS
    global TBENCH_NCLIENTS
    global TBENCH_SERVER
    
    serverOut = runRemoteCommand(f"TBENCH_WARMUPREQS={TBENCH_WARMUPREQS} TBENCH_MAXREQS={TBENCH_MAXREQS} TBENCH_NCLIENTS={TBENCH_NCLIENTS} ~/bayop/tailbench/img-dnn/img-dnn_server_networked -r 10 -f /data/tailbench.inputs/img-dnn/models/model.xml -n 100000000", TBENCH_SERVER)
    time.sleep(5)

    clientOut = runLocalCommand(f"TBENCH_QPS={TBENCH_QPS} ~/bayop/tailbench/img-dnn/img-dnn_client_networked")
    print("Client Output:")
    for out in clientOut.communicate():
        print(str(out.strip()), end=" ")
    print("")

    print("Server Output:")
    for out in serverOut.communicate():
        print(str(out.strip()), end=" ")
    print("")
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--qps", help="QPS")
    parser.add_argument("--warmup", help="Warmup requests")
    parser.add_argument("--maxq", help="Max requests")
    parser.add_argument("--nclients", help="Number of clients")

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
    print(f"TBENCH_WARMUPREQS={TBENCH_WARMUPREQS} TBENCH_MAXREQS={TBENCH_MAXREQS} TBENCH_NCLIENTS={TBENCH_NCLIENTS} TBENCH_QPS={TBENCH_QPS} TBENCH_SERVER={TBENCH_SERVER}")
    
    run()
