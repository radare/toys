#!/bin/sh
# etherpad-lite command line utility
# author pancake<nopcode.org>
# date 2011-11-16

DB=var/dirty.sqlite
LOG=var/log.txt

q() {
	echo "$@" | sqlite3 ${DB}
}

case "$1" in
start)
	if (sh $0 check > /dev/null); then
		echo already running
		exit 1
	else
		echo starting...
		sed -e 's,bin/install,#bin/install,' bin/run.sh > bin/run.sh.x
		sh bin/run.sh.x > ${LOG} &
		sleep 2
	fi
	;;
run)
	sed -e 's,bin/install,#bin/install,' bin/run.sh > bin/run.sh.x
	sh bin/run.sh.x
	;;
stop)
	if (sh $0 check > /dev/null); then
		echo stopping...
		pkill -INT -f "node server.js"
		sleep 2
	else
		echo already running
		exit 1
	fi
	;;
check)
	pgrep -f "node server.js" > /dev/null
	r=$?
	if [ $r = 0 ]; then
		echo "running"
	else
		echo "stopped"
	fi
	exit $r
	;;
restart)
	sh $0 stop
	sh $0 start
	;;
ls|list)
	q "select key from store where key like 'pad2readonly:%';" | cut -d : -f 2
	;;
revs)
	n="$2"
	if [ -n "$n" ]; then
		q "select key from store where key like 'pad:$n:revs:%';" 
	else
		echo "Usage $0 revs [padname]"
	fi
	;;
rm)
	n="$2"
	if [ -n "$n" ]; then
		q "delete from store where key like 'pad:$n%';" 
		q "delete from store where key like 'pad2readonly:$n';" 
	else
		echo "Usage $0 rm [padname]"
	fi
	;;
cat)
	q "select value from store where key='pad:$2';" | \
		sed -e 's,\\n,\n,g' | \
		sed -e 's,\\\\,\\,g' | \
		sed -e 's,{"atext":{"text":",,' | \
		sed -e 's/","attribs":.*//'
	;;
clean)
	sh $0 check >/dev/null
	r=$?
	[ $r = 0 ] && sh $0 stop
	printf " + removed pad revisions: "
	q "select count(key) from store where key like 'pad:%:revs:%';"
	q "delete from store where key like 'pad:%:revs:%';"

	printf " + removed chat entries: "
	q "select count(key) from store where key like 'pad:%:chat:%';"
	q "delete from store where key like 'pad:%:chat:%';"

	printf " + remove empty pads: "
	q "select count(key) from store where value like '%Welcome to Etherpad Lite%';"
	q "delete from store where value like '%Welcome to Etherpad Lite%';"
	[ $r = 0 ] && sh $0 start
	# we cant remove the author information
	#q "delete from store where key like '%uthor:%';"
	;;
*)
	echo "Usage: $0 [cmd] [arg]"
	echo "   start/stop  start or stop etherpad-lite server"
	echo "   restart     stop and start the server"
	echo "   ls          list all pads"
	echo "   revs [pad]  list revisions of given pad"
	echo "   cat [pad]   show contents of pad"
	echo "   rm [pad]    remove pad by name"
	echo "   clean       remove all revisions, author and chats"
	;;
esac
