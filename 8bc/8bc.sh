#!/bin/sh
# 8bc - GPL3 - nibble <develsec.org> 2009
# Play 8BitCollective stream

wget -q -O - http://8bc.org/rss/music | \
grep "http://www.8bc.org/items/music/" | \
sed 's/.*\(http.*\)" l.*/\1/' > /tmp/8bc.pls
mplayer -playlist /tmp/8bc.pls
