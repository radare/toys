#!/bin/sh
Xephyr -screen 1200x600 -ac :1 &
sleep 2
export DISPLAY=:1
gnome-session &
xterm -bg black -fg gray -e "sh server.sh"
exit 0


Xnest -geometry 740x400 -ac :1 &
export DISPLAY=:1
icewm &
xterm -fn 10x20 -bg black -fg white
