#!/bin/sh
if [ -z "`uname -m | grep -e iPad -e iPod -e iPhone`" ]; then
	echo "This program only runs in iOS"
	exit 1
fi
. ./CONFIG
if [ "$1" = "-h" ]; then
	echo "Usage: APPS=... iobs [dirname]"
	echo " APPS environ var is the list of apps to backup (default apps/*)"
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
if [ -n "${APPS}" ]; then
	OAPPS=""
	for a in ${APPS} ; do
		OAPPS=$(printf "$APPS apps/$a")
	done
	APPS=$OAPPS
else
	APPS=$(ls apps/*)
fi
for a in $APPS ; do
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
