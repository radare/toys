#!/bin/sh
case "$1" in
enable|1|on)
	if [ -e /usr/libexec/afcd.disabled ]; then
		mv /usr/libexec/afcd.disabled /usr/libexec/afcd
	fi
	;;
disable|0|off)
	if [ -e /usr/libexec/afcd ]; then
		mv /usr/libexec/afcd /usr/libexec/afcd.disabled
	fi
	killall afcd
	;;
-h|help|?)
	echo "Usage: afc.sh [off|on|status]"
	;;
status|*)
	if [ -e "/usr/libexec/afcd" ]; then
		echo "enabled"
	else
		echo "disabled"
	fi
	;;
esac
