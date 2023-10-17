#! /bin/bash

cache_file="$HOME/.tor-checklist"
ip="$1"

if [[ -z ${ip} ]]; then
    echo "Usage: $0 <ip>"
    exit 1
fi

now=$(date +%s)

if [[ -e ${cache_file} ]]; then
    cache_time=$(gstat -c %X ${cache_file})
else
    cache_time=0
fi

if [[ $((now - cache_time)) -gt 3600 ]]; then
    wget -q -O ${cache_file} https://check.torproject.org/torbulkexitlist
fi

if grep -qFx ${ip} ${cache_file}; then
    echo "${ip} found in Tor exit node list"
else
    echo "${ip} not found in exit node list"
fi
