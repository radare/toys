#!/bin/sh

TURNS=999999999
MONEY=999999999

cd /var/mobile/Applications/
cd */tripletown.app
cd ../Library/Preferences

T=com.spryfox.tripletown.plist
plutil $T

[ -n "$1" ] && exit 0

kill -9 `ps aux| grep tripletown| grep -v grep|awk ' {print $2}'`


plutil -key scorpionfish -int ${TURNS} $T
plutil -key triggerfish -int ${MONEY} $T
