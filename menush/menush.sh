#!/bin/sh
#
# Usage: sh menush.sh [-]
#

control_c() {
:
}
trap control_c 2

STDIN=0
[ "$1" = "-" ] && STDIN=1
ROOT=$PWD
if [ -d "Root" ]; then
ROOTDIR="Root"
else
ROOTDIR="${HOME}/.menush/Root"
fi
if [ -x "eread" ]; then
	export PATH="${ROOT}:${PATH}"
fi

if [ ! -d "${ROOTDIR}" ]; then
	echo "Cannot find '${ROOTDIR}' directory here."
	echo ""
	printf "Do you want to fetch the initial menu tree? (Y/n) "
	A=`eread`
	case $A in
	"intro"|"Y"|"y")
# c&p hack (Root/u/exec)
cd /tmp
wget http://news.nopcode.org/menush.tar.gz
cd ${HOME}
if [ "`tar --help| grep GNU`" ]; then
tar xzvf /tmp/menush.tar.gz menush/
else
mkdir -p menush
tar xzvf /tmp/menush.tar.gz menush/* \
        menush/*/* \
        menush/*/*/* \
        menush/*/*/*/*
fi
rm -rf .menush
mv menush .menush
rm -rf /tmp/menush.tar.gz
# c&p hack
		echo "Fetch done. let'z go in."
		sleep 2
		;;
	*)
		echo "Abort"
		exit 1
		;;
	esac
fi
cd ${ROOTDIR}
level=0

#
# eread way
#

if [ -z "$1" ]; then
while : ; do
	STR=""
	for A in * ; do
		if [ -d "${A}" ]; then
			TITLE="(no title)"
			[ -e "${A}/title" ] && TITLE=`cat ${A}/title`
			STR="${STR} \"${A}  ${TITLE}\""
		fi
	done
	A=`eval eread -m ${STR} | cut -c 1`
	echo $A
	case "${A}" in
	"q")
		if [ ! "${level}" = "0" ]; then
			level=$(($level-1))
			cd ..
		fi
		;;
	"")
		exit 0
		;;

	*)
		if [ -d "${A}" ]; then
			if [ -f "${A}/exec" ]; then
				sh ${A}/exec
			else
				level=$(($level+1))
				cd ${A}
			fi
		fi
		;;
	esac
done
fi

#
# bash way
#

display() {
	[ 1 = "${STDIN}" ] && return
	echo
	echo "--[ menu ]--( 'q' exit menu, 'Q' quit program )--"
	for A in * ; do
		if [ -d "${A}" ]; then
			TITLE="(no title)"
			[ -e "${A}/title" ] && TITLE=`cat ${A}/title`
			echo "  $A   ${TITLE}"
		fi
	done
}

while : ; do
	display
	A=`eread` #read -n 1 A
	echo
	case "${A}" in
	"q")
		if [ ! "${level}" = "0" ]; then
			level=$(($level-1))
			cd ..
		fi
		;;
	"Q")
		exit 0
		;;

	*)
		if [ -d "${A}" ]; then
			if [ -f "${A}/exec" ]; then
				sh ${A}/exec
			else
				level=$(($level+1))
				cd ${A}
			fi
		fi
		;;
	esac
done
