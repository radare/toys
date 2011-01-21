all:
	#gcc -pedantic -g -Werror -Wall -lresolv resmx.c llist.c
	gcc -DMX resmx.c llist.c -lresolv -o mx
	gcc  resmx.c llist.c -lresolv -o mxlist

install:
	cp mx /usr/bin
	cp mxlist /usr/bin

clean:
	rm -f a.out *.o mx mxlist
