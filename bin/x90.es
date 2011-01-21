#!/bin/sh
case "$1" in
"")
	echo "Usage: x90.es [url]"
	;;
"-l")
	curl http://x90.es/rss.php | grep '<description>' | sed -e 's,<,>,g' | cut -d '>' -f 3
	;;
*)
	curl "http://x90.es/api.php?action=shorturl&url=$@" ; echo
	;;
esac
