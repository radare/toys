control_c() {
	echo "killing shoter..."
	kill -9 `cat pid`
	pkill scrot
	pkill thttpd
	exit 1
}

trap control_c 2
sh shoter.sh &
/usr/sbin/thttpd -d /home/pancake/prg/screencast -p 8123
echo "listening at port 8123..."
while : ; do sleep 1 ; done

