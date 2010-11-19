#!/bin/sh
for a in /Applications/*.app ; do
	prg=$(echo $a | cut -d / -f 3)
	printf "$prg\t$a\n"
done
for a in /var/mobile/Applications/*/*.app ; do
	prg=$(echo $a | cut -d / -f 6)
	printf "$prg\t$a\n"
done
