#!/bin/sh
#
# test.sh
#

for script in $(find examples -type f -name "*.pks");
do
	./asc-cli b ~/RH/FR.gba $script || exit 1
done

