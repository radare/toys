#!/bin/sh
[ -z "$JARPATH" ] && JARPATH="/usr/pkg/share/classpath:/usr/pkg/lib/java"
JARPATH=`echo $JARPATH | awk '{ gsub(/:/," "); print $0}'`

for A in $JARPATH ; do
  for B in `ls $A/*.jar 2> /dev/null` ; do
    CLASSPATH=$B:$CLASSPATH
  done
done
echo $CLASSPATH
