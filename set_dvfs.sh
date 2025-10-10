#!/bin/bash

set -x

function userspace
{
    sudo /users/$(whoami)/eeflink/cpufreq-set-all -g userspace
    sudo cpufreq-info
}

# conservative, ondemand, userspace, powersave, performance, schedutil 
function ondemand
{
    sudo /users/$(whoami)/eeflink/cpufreq-set-all -g ondemand
    sudo cpufreq-info
}

function conservative
{
    sudo /users/$(whoami)/eeflink/cpufreq-set-all -g conservative
    sudo cpufreq-info
}

function powersave
{
    sudo /users/$(whoami)/eeflink/cpufreq-set-all -g powersave
    sudo cpufreq-info
}

function performance
{
    sudo /users/$(whoami)/eeflink/cpufreq-set-all -g performance
    sudo cpufreq-info
}

function schedutil
{
    sudo /users/$(whoami)/eeflink/cpufreq-set-all -g schedutil
    cpufreq-info
}

"$@"
