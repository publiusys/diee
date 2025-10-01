parallel-ssh -i -t 0 -h ~/.psshfiles sudo apt-get install -y cpufrequtils msr-tools python3-pip uuid-dev autotools-dev automake tcl libtool libreadline-dev libgtop2-dev bison swig scons libevent-dev gengetopt libzmq3-dev libevent-dev numactl

echo off | sudo tee /sys/devices/system/cpu/smt/control
sudo sysctl vm.nr_hugepages=4096
