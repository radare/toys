#!/bin/sh
FEED=http://chipmusic.org/music/rss/feed.xml
wget -q -O - ${FEED} | grep "media.chipmusic.org" | grep mp3 | cut -d '"' -f 2 > /tmp/cm.pls
mplayer -playlist /tmp/cm.pls
