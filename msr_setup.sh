#!/bin/bash

sudo groupadd msr
sudo chgrp msr /dev/cpu/*/msr
sudo chmod g+rw /dev/cpu/*/msr
sudo usermod -aG msr hand32
sudo newgrp msr

