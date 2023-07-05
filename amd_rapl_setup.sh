#!/bin/bash

set -x

CWD=$(pwd)

cd /etc/systemd/system && sudo ln -s ~/bayop/rapl_service/amd_rapl_log.service rapl_log.service && cd $CWD
