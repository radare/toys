#!/bin/sh
#
# Enable DuckDuckGo search engine for MobileSafari on iOS devices
#
# date: 2012-04-21
# author: pancake<nopcode.org>
#

USR_PLIST=/var/mobile/Library/Safari/SearchEngines.plist
SYS_PLIST=/private/var/stash/Applications/MobileSafari.app/SearchEnginesFallback.plist

plist2binary() {
	plutil -convert binary1 $1 >/dev/null
}
plist2xml() {
	plutil -convert xml1 $1 >/dev/null
}

setDdg() {
	cp $1 $1.xml
	plist2xml $1.xml
	x=`cat <<EOF
        <dict>
                        <key>ScriptingName</key>
                        <string>DuckDuckGo</string>
                        <key>SearchURLTemplate</key>
                        <string>https://duckduckgo.com/?q={searchTerms}</string>
                        <key>ShortName</key>
                        <string>DDG</string>
                        <key>SuggestionsURLTemplate</key>
                        <string></string>
	</dict>
EOF`
	awk -v x="$x" '{if (/^\t<\/array/) { print x"</array>"; } else {print;}}' $1.xml > $1
	plist2binary $1
}

unsetDdg() {
	cp $1 $1.xml
	plist2xml $1.xml
	awk '
	BEGIN {
		TMP="";
		SKIPUNTIL=0;
	} {
		if (SKIPUNTIL==1) {
			if (/dict/) {
				SKIPUNTIL=0
			}
		} else {
			if (/<dict>/) {
				TMP=TMP""$0;
			} else {
				if (TMP=="") {
					print;
				} else {
					TMP=TMP"\n"$0;
					if (/string/){
						if (/DuckDuck/) {
							TMP=""
							SKIPUNTIL=1
						} else {
							print TMP
							TMP=""
						}
					}
				}
			}
		}
	}' $1.xml > $1
	plist2binary $1
}

hasDdg() {
	if [ -e $USR_PLIST ]; then
		plist2xml $USR_PLIST
		grep -q DDG $USR_PLIST
	else
		if [ -e $SYS_PLIST ]; then
			plist2xml $SYS_PLIST
			grep -q DDG $SYS_PLIST
		else
			return 1
		fi
	fi
}

killSafari() {
	killall MobileSafari 2>/dev/null
}

enableDdg() {
	hasDdg && exit 0
	rm -f $USR_PLIST
	killSafari
	setDdg $SYS_PLIST
	cp $SYS_PLIST $USR_PLIST
}

disableDdg() {
	hasDdg || exit 0
	rm -f $USR_PLIST
	killSafari
	unsetDdg $SYS_PLIST
	cp $SYS_PLIST $USR_PLIST
}

[ ! -e ${SYS_PLIST}.orig ] && \
	cp -f ${SYS_PLIST} ${SYS_PLIST}.orig

case "$1" in
"")
	hasDdg && echo enabled || echo disabled
	;;
"enable")
	enableDdg
	;;
"disable")
	disableDdg
	;;
*)
	echo "Usage: ddgios.sh [enable|disable]"
	exit 1
	;;
esac
