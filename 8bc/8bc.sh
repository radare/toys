#!/bin/sh
# 8bc - GPL3 - nibble <develsec.org> 2009
# Play 8BitCollective stream

wget -q -O - http://www.8bitcollective.com/rss/music | \
grep "http://www.8bitcollective.com/items/music/" | \
sed 's/.*\(http.*\)" l.*/\1/' > /tmp/8bc.pls
mplayer -playlist /tmp/8bc.pls
