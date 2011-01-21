#!/bin/sh
cd /home/pancake/prg/8bc
U=`xsel`
if [ -n "`echo $U | grep ^Playing`" ]; then
	U=`echo $U | cut -d ' ' -f 2-| sed -e s,.$,,`
fi
wget -c $U
