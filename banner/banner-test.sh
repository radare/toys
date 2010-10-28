#!/bin/sh
TEXT=$1
[ -z "${TEXT}" ] && TEXT=radare
for a in $(cat banner-fonts) ; do
  echo "$a:"
  sh banner.sh $TEXT $a
done
