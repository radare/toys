#!/bin/sh
echo $$ > pid
while : ; do
	#sleep 1
	sleep 1
	#xwd -root | convert -resize 80% -quality 50 - shot.tmp.jpg
	scrot -q 30 shot.tmp.jpg
	./fehscale shot.tmp.jpg shot2.tmp.jpg 2>&1 >/dev/null
	printf "."
	mv shot2.tmp.jpg shot.jpg
done
