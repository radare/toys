#!/bin/sh
if [ "$1" = "-h" ]; then
  echo "Usage: 4chan.sh [-ch] [pages]"
  echo "  -c is for clean, -h for help."
  echo "while : ; do ./4chan.sh -c ; sleep 60 ; done"
  exit 0
fi
b=b; [ -n "$BOARD" ] && b=$BOARD
if [ "$1" = "-c" ]; then
  CUR=$(ls *.jpg *.png *.gif)
#  rm -f *.jpg *.png *.gif
  shift
else
  CUR=""
fi
[ -z "$(pidof eog)" ] && eog -s -f . &
num=$1
[ -z "$num" ] && num=0
echo "[4ch] fetching /$b/.."
curl -s curl http://boards.4chan.org/$b/ > a
for a in $(seq 1 $num) ; do
	curl -s curl http://boards.4chan.org/$b/$a >> a
done
cat a | grep -e jpg -e gif -e png | grep images.4chan | \
	perl -ne 'if (/href="([^"]*)"/) { $p=$1; if ($1=~/http/) {print "$p\n"}}' > b
echo "[4ch] downloading pics.."
for a in $(cat b); do
echo $a
  f=$(basename $a)
  if [ ! -f $a ]; then
    echo " * $a"
    rm -rf tmp
    mkdir -p tmp
    cd tmp
    wget -q $a 2>&1
    mv * ..
    cd ..
  fi
done
[ -n "$CUR" ] && rm -f ${CUR}
echo "[4ch] done"
