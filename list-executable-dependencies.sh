#! /bin/bash

if [[ -z $1 ]]; then
	echo "Usage: $0 <executable>"
	exit 1
fi

ldd $1 | awk '/=>/{print $(NF-1)}' | apt-file search --from-file - --package-only | xargs aptitude show | grep -e "^Package:" -e "^State:" | grep -B 1 "^State: installed" | grep "^Package:" | awk '{ print $2 }'
