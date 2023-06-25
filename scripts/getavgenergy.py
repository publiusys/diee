import sys
from statistics import mean

fname = sys.argv[1]

with open(fname) as file:
    server_rapl_log = [float(line.rstrip()) for line in file]
print(f"{fname} avg_watts ", mean(server_rapl_log[15:25]))
