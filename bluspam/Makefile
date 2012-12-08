INSTALL=cp
PREFIX=/usr
#OBJ=bluspam_engine.o
OBJ=engine.o window.o config.o list.o main.o bluspam_engine.o
VAL=*.vala
BIN=bluspam

%.o: %.vala
	valac -c -o $*.o --pkg gtk+-2.0 $*.vala

all:
	valac -o ${BIN} --pkg gtk+-2.0 *.vala bluspam_engine.c
	cd sh/opush && make

all2: ${OBJ}
	#valac -c -o ${BIN} --pkg gtk+-2.0 *.vala
	gcc -O3 *.o -o ${BIN} `pkg-config --libs --cflags gtk+-2.0`
	#valac *.o -o ${BIN} --pkg gtk+-2.0

clean:
	-rm -f ${OBJ} ${BIN}
	cd sh/opush && make clean

fast:
	valac --disable-checking --disable-assert -o a.out --pkg gtk+-2.0 *.vala

c:
	valac -g --pkg gtk+-2.0 *.vala
#	mv window.c window.c.orig &&\
#	cat window.c.orig | ${FIX} > window.c
	valac *.c --save-temps --pkg gtk+-2.0 -o a.out

install:
	cat bluspam.sh | sed -e 's,##PREFIX##,${PREFIX},g' > ${PREFIX}/bin/bluspam
	chmod +x ${PREFIX}/bin/bluspam
	mkdir -p ${PREFIX}/libexec/bluspam
	cp -rf bluspam ${PREFIX}/libexec/bluspam
	cp -rf sh ${PREFIX}/libexec/bluspam
	cp -rf logo.png ${PREFIX}/libexec/bluspam
	chmod -R 777 ${PREFIX}/libexec/bluspam
