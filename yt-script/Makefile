VERSION=0.2
PREFIX?=/usr/local
CFLAGS+=-DVERSION=\"${VERSION}\"
BIN=yt-script
OBJ=yt-script.o

all: ${OBJ}
	gcc ${LDFLAGS} ${OBJ} -lutil -o ${BIN}

clean:
	-rm -f ${BIN} ${OBJ}

install:
	cp yt-script ${PREFIX}/bin
	chmod 0755 ${PREFIX}/bin/yt-script
	cp yt-termcast ${PREFIX}/bin
	chmod 0755 ${PREFIX}/bin/yt-termcast
