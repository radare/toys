echo $$ > pid
while : ; do
sleep 1
scrot -q 15 shot.tmp.jpg
mv shot.tmp.jpg shot.jpg
done
