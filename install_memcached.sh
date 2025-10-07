#!/bin/bash

cd ~ && wget https://github.com/memcached/memcached/archive/refs/tags/1.6.39.tar.gz && tar -xf 1.6.39.tar.gz && cd ~/memcached-1.6.39 && ./autogen.sh && ./configure && make -j
