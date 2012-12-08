#!/bin/sh
# iPod2G semi-tethered boot
# --pancake

stage=$1
files=../semi-tether


echo FOLLOW THE INSTRUCTIONS... PRESS ENTER TO START
read A
echo
echo PRESS 10 SECONDS POWER AND FRONT BUTTON
echo
sleep 10
echo
echo DROP POWER BUTTON
echo
sleep 10
echo DROP FRONT BUTTON
echo ---
echo PRESS ANY KEY
read A

#cd iRecovery
if [ -z "$stage" ]; then
sudo ./iRecovery -f ${files}/iBSS211.dfu 

echo PLEASE UNPLUG/REPLUG THE IPOD
echo ---
echo PRESS ANY KEY
read A

fi

echo "[xx] Sending RedSn0w..."
sudo ./iRecovery -s << EOF
arm7_stop
mw 0x9000000 0xe59f3014
mw 0x9000004 0xe3a02a02
mw 0x9000008 0xe1c320b0
mw 0x900000c 0xe3e02000
mw 0x9000010 0xe2833c9d
mw 0x9000014 0xe58326c0
mw 0x9000018 0xeafffffe
mw 0x900001c 0x2200f300
arm7_go
/exit
EOF

sleep 3

echo "[xx] Stopping arm7 cpu..."
sudo ./iRecovery -s << EOF
arm7_stop
/exit
EOF
sleep 3

echo "[xx] Sending patched iBSS 2.2.1..."
sudo ./iRecovery -f ${files}/iBSS221pwn.dfu 
echo "[xx] Go into recovery mode..."
sudo ./iRecovery -s << EOF
go
/exit
EOF

# REPLUG HERE?
## echo PLEASE UNPLUG/REPLUG THE IPOD
## read A
sleep 5

echo "[xx] Sending semi-tethered iBoot 2.2.1.."
sudo ./iRecovery -f ${files}/iBoot221semi.img3

echo "[xx] Go into recovery mode..."
sudo ./iRecovery -s << EOF
go
/exit
EOF

sleep 5
echo "[xx] Configuring environment"
sudo ./iRecovery -s << EOF
setenv boot-path /System/Library/Caches/com.apple.kernelcaches/kernelcache.s5l8720p
fsboot
/exit
EOF

sleep 5
echo "[xx] Here we go!"
sudo ./iRecovery -s << EOF
go
/exit
EOF
