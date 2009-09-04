#!/bin/sh

RET=`echo "blues
chillout
drum and bass
jazz
techno
punk
reggae
stop" | dmenu`

[ -z "$RET" ] && exit

pkill mplayer

[ "$RET" = "stop" ] && exit

shoutcast.pl "$RET" $(($RANDOM%8)) &
