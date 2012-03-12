#!/bin/sh
A=$1
shift
if [ -z "$1" ]; then
	echo "Usage: waitfor [proc] [cmd]"
	echo "example: waitfor safari gdb --pid"
	exit 1
fi
export A
while : ; do
	n=`ps auxw| grep -i $A | grep -v grep |grep -v waitfor | awk '{print $2}'`
	if [ -n "$n" ]; then
		echo "PID=$n"
		exec $@ $n
	fi
done
