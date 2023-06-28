sudo LD_LIBRARY_PATH=~/bayop/tailbench/xapian/xapian-core-1.2.13/install/lib TBENCH_NCLIENTS=2 TBENCH_WARMUPREQS=1000 TBENCH_MAXREQS=10000 chrt -r 99 ./xapian_networked_server -n 10 -d /data/tailbench.inputs/xapian/wiki -r 1000000000

sudo TBENCH_CLIENT_THREADS=10 TBENCH_SERVER_PORT=8080 TBENCH_SERVER=192.168.1.20 TBENCH_QPS=1000 TBENCH_MINSLEEPNS=100000 TBENCH_TERMS_FILE=/data/tailbench.inputs/xapian/terms.in chrt -r 99 ./xapian_networked_client
