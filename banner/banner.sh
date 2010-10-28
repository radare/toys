#!/bin/sh
TEXT=$1
FONT=$2
[ -z "${TEXT}" ] && TEXT=hello
[ -z "${FONT}" ] && FONT=ogre
curl -s "http://www.network-science.de/ascii/ascii.php?TEXT=$TEXT&FONT=${FONT}&RICH=no" | \
	sed -e 's,&gt;,>,g' -e 's,&lt;,<,g' -e 's,&quot;,",g' -e 's,&amp;,&,g' | \
	awk 'BEGIN{a=0}{if(/TD/&&/PRE/)a=1; if (/white text/)a=0; gsub(/^.*PRE>/,//); gsub("1","");if (a) print;}'
