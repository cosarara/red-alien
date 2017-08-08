#!/bin/sh
#
# test.sh
#

for script in $(find examples -type d -path "*mustfail" -prune -o -type f -name "*.pks" -print);
do
	./asc-cli b ~/RH/FR.gba $script || exit 1
done

