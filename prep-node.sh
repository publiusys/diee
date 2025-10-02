#!/bin/bash

#set -x

CWD=$(pwd)
GENIUSER=`geni-get user_urn | awk -F+ '{print $4}'`

sudo apt-get update
sudo apt install msr-tools -y

# disable HyperThreads
echo off | sudo tee /sys/devices/system/cpu/smt/control

# disable TurboBoost
echo "1" | sudo tee /sys/devices/system/cpu/intel_pstate/no_turbo

# disable irq rebalance
sudo killall irqbalance

# set irq affinity - make sure receive/transmit queues are mapped to the same core
ieth=$(ifconfig | grep -B1 10.10.1 | grep -o "^\w*")
sudo $CWD/intel_set_irq_affinity.sh -x all ${ieth}

# sets hostname depending on IP
mip=$(ifconfig | grep -B1 10.10.1 | grep inet | grep -oP 'inet \K(\d+\.\d+\.\d+\.\d+)')
case $mip in

    "10.10.1.1")
	sudo hostname client-$mip
	;;

    "10.10.1.2")
	sudo hostname server-$mip
	;;
    
    *)
	sudo hostname agent-$mip
	#echo -n "Unknown IP: ${ieth}"
	;;
esac

# this is causing firmware issues on c6220 nodes, disable for now
sudo rmmod mlx4_ib
sudo rmmod mlx4_core

# list current status
sudo ufw status

# setup firewall
sudo ufw allow ssh

# allow connections from the following IP
sudo ufw allow from 10.10.1.1
sudo ufw allow from 10.10.1.2
sudo ufw allow from 10.10.1.3
sudo ufw allow from 10.10.1.5
sudo ufw allow from 10.10.1.6
sudo ufw allow from 10.10.1.7
sudo ufw allow from 10.10.1.8
sudo ufw allow from 10.10.1.9
sudo ufw allow from 10.10.1.10

# deny everything else
sudo ufw default allow outgoing
sudo ufw default deny incoming

# enable ufw
echo y | sudo ufw enable
sudo ufw status

# disable redundant logging messages
sudo ufw logging off

# enable MSR to set DVFS statically
sudo modprobe msr
# lets run without sudo
sudo setcap cap_sys_rawio=ep /usr/sbin/rdmsr 
sudo setcap cap_sys_rawio=ep /usr/sbin/wrmsr
sudo setcap cap_net_admin+ep /usr/sbin/ethtool

# setup password-less ssh between nodes
sudo $CWD/prep-ssh.sh

# allow msr without sudo
sudo groupadd msr
sudo chgrp msr /dev/cpu/*/msr
sudo ls -l /dev/cpu/*/msr
sudo chmod g+rw /dev/cpu/*/msr
sudo usermod -aG msr $GENIUSER

echo "🔴🔴  Re-login for msr group changes to take effect 🔴🔴"
sudo newgrp msr
