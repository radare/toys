#!/bin/sh
. ./CONFIG
if [ "$1" = "-h" ]; then
	echo "Usage: iobs [dirname]"
	echo " default: backup all known apps"
	echo " dirname: restore app preferences from given dir"
	exit 0
fi
if [ -n "$1" ]; then
	BDIR=${PWD}/$1
	if [ ! -d "${BDIR}" ]; then
		echo "Oops: cannot find ${BDIR}"
		exit 1
	fi
else
	BDIR=${PWD}/$(date +%Y%m%d)
fi
export BDIR
for a in apps/* ; do
	SKIPPED=0
	for b in ${SKIP} ; do
		if [ "$a" = "apps/$b" ]; then
			SKIPPED=1
			break
		fi
	done
	if [ $SKIPPED = 0 ]; then
		sh $a $1
	fi
done

echo "======================================"
echo "NOTE: Remember to backup dTunes music:"
du -hs /var/mobile/Library/Downloads
echo "======================================"
