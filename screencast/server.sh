#!/bin/sh
PORT=8123
WWW=${PWD}

oneko/oneko

control_c() {
	echo "killing shoter..."
	kill -9 `cat pid`
	pkill scrot
	pkill thttpd
	pkill lighttpd
	pkill oneko
	exit 1
}

run_httpd_server() {
	#thttpd -d ${WWW} -p ${PORT}
	#darkhttpd ${WWW}
	#quark
	lighttpd -f lighttpd.conf
}

trap control_c 2
sh shoter.sh &

run_httpd_server
echo "listening at port 8123..."
while : ; do sleep 1 ; done
