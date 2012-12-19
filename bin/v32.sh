#!/bin/sh
# initialize and run 32bit programs on voidlinux32
p=${HOME}/void32
LD_LIBRARY_PATH=$p/usr/lib
export LD_LIBRARY_PATH

case "$1" in
-u|umount)
	for a in /dev /sys /proc /home /tmp ; do
		sudo umount $p/$a
	done
	;;
-m|mount)
	for a in /dev /sys /proc /home /tmp ; do
		sudo mount -o bind $a $p/$a
	done
	;;
-i|init)
	sudo setcap cap_sys_chroot=ep /usr/bin/chroot 
	fakeroot linux32 xbps-install -r $p base-system
	;;
*)
	cd $p/${HOME}
	eval chroot $p bash -c "'cd;$@'"
	;;
esac
