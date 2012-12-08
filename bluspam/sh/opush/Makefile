#
# UNrooted.net example code
#
# Minimal Makefile used to build my Bluez OBEX example.  The generated 
# executable 'ussp-push' can be used to push files using OBEX over RFCOMM with
# the Bluez Linux Bluetooth stack.  You should be able to just 'make' directly
# without any setup.
#

#
# These are the default paths the openobex package installs under.  Hack as
# necessary to reflect your setup.
#

OBEXINC=-I/usr/local/include
OBEXLIB=-L/usr/local/lib -lopenobex -lbluetooth

CFLAGS:=${CFLAGS} -Wall

OBEX_INCLUDES=obex_macros.h obex_socket.h obex_main.h obex_sdp.h

#
# The make rules.. basically just two files here plus the openobex and glib
# libraries and we can make the executable.
#

all: opush

opush: obex_main.o obex_socket.o obex_sdp.o
	gcc obex_main.o obex_socket.o obex_sdp.o ${OBEXLIB} -o opush
 
obex_main.o: obex_main.c ${OBEX_INCLUDES}
	gcc ${CFLAGS} ${OBEXINC} -c obex_main.c -o obex_main.o

obex_socket.o: obex_socket.c ${OBEX_INCLUDES}
	gcc ${CFLAGS} ${OBEXINC} -c obex_socket.c -o obex_socket.o

obex_sdp.o: obex_sdp.c ${OBEX_INCLUDES}
	gcc ${CFLAGS} ${OBEXINC} -c obex_sdp.c -o obex_sdp.o

clean:
	@rm -rf opush *.o *~

