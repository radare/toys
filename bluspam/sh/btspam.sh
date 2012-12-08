#!/bin/sh

TOSCAND="" # to scan devices
HANDLED="" # yet found devices
BCASTED="" # yet bcasted devices
NAME="Ricard Martinez"
NAME="Gracia"

:> log

control_c(){
echo "Final report:"
echo "============="
echo
echo "Found devices"
echo " ${HANDLED}"
echo
echo "Failed to send"
echo " ${TOSCAND}"
echo
echo "Spammed devices"
echo " ${BCASTED}"
exit 0
}

trap control_c 2

echo "BT-GraciaCktivism"
echo

hciconfig hci0 up
hciconfig hci0 name "${NAME}"

if [ ! $? = 0 ]; then
echo Failed to up hci0
exit 1
fi


# Get non-handled addresses
do_scan() {
echo "Scanning..."
BTADDRS=`hcitool scan | awk '{ if(!/Scan/) { print $1; } }'` # new found devices
for A in ${BTADDRS}; do
FOUND=0
for B in ${HANDLED}; do
if [ "${B}" = "${A}" ]; then
FOUND=1
break;
fi
done
# append it :D
if [ "${FOUND}" = "0" ]; then
echo "New device ${A}"
HANDLED="${HANDLED} ${A}"
TOSCAND="${TOSCAND} ${A}"
fi
done
}

do_send_file() {
ADDR=$1
echo "Sending file to ${ADDR}"
ussp-push ${ADDR}@9 file prego.txt >> log
return $?
}

while : ; do
QUEUE=""
do_scan
for A in ${TOSCAND}; do
do_send_file ${A}
if [ "$?" = "0" ]; then
echo "Sent OK"
BCASTED="${BCASTED} ${A}"
else
echo "Sent FAILED. Enqueueing ${A}"
QUEUE="${QUEUE} ${A}"
fi
done

TOSCAND="${QUEUE}"
done
