#!/bin/sh
#
# test.sh
#

for script in $(find examples -type d -path "*mustfail" -prune -o -type f -name "*.pks" -print);
do
	cp ~/RH/Ruby.RO.gba ~/RH/test.gba
	chmod +w ~/RH/test.gba
	echo "########### INITIAL COMPILATION"
	./asc-cli c ~/RH/test.gba $script || exit 1
	checksum=$(md5sum ~/RH/test.gba)
	echo "########### DECOMPILATION"
	./asc-cli d ~/RH/test.gba 0x800000 > tmp.pks || exit 1
	echo "########### RECOMPILATION"
	./asc-cli c ~/RH/test.gba tmp.pks || exit 1
	checksum2=$(md5sum ~/RH/test.gba)
	if [ "$checksum" != "$checksum2" ]; then
		echo $checksum
		echo $checksum2
		exit 2
	fi
done

