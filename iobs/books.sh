#!/bin/sh
if [ -z "$1" ]; then
	echo "cd /var/mobile/Media/Books/Purchases"
	echo "Usage: epub [dir]"
	exit 1
fi
while : ; do
	[ -z "$1" ] && break
	if [ -e $1/content.opf ]; then
		printf "$1\t"
		grep :title "$1"/content.opf | sed -e 's,<[^>]*.,,g'
	else if [ -f "$1"/iTunesMetadata.plist ]; then
		printf "$1\t"
		plutil -key itemName "$1"/iTunesMetadata.plist 
	fi ; fi
	shift
done
