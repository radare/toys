/* Simple OpenOBEX server for Bluez+OpenOBEX */
/* link with libmisc.a from OPENObex-apps and libopenobex from OpenOBEX */
/* venglin@freebsd.lublin.pl */


#include <stdio.h>
#include <stdlib.h>
#include <netinet/in.h>

#include <openobex/obex.h>
//#include <bluetooth/bluetooth.h>
#include <bluetooth/rfcomm.h>

typedef union {
#ifdef HAVE_IRDA
        struct sockaddr_irda irda;
#endif /*HAVE_IRDA*/
        struct sockaddr_in   inet;
        struct sockaddr_rc   rfcomm;
} saddr_t;


typedef struct obex_transport_t {
        int     type;
        int connected;  /* Link connection state */
        unsigned int    mtu;            /* Tx MTU of the link */
        saddr_t self;           /* Source address */
        saddr_t peer;           /* Destination address */
} obex_transport_t;

typedef struct obex {
        uint16_t mtu_tx;                        /* Maximum OBEX TX packet size */
        uint16_t mtu_rx;                        /* Maximum OBEX RX packet size */
        uint16_t mtu_tx_max;            /* Maximum TX we can accept */

        int fd;                 /* Socket descriptor */
        int serverfd;
        int writefd;            /* write descriptor - only OBEX_TRANS_FD */
        unsigned int state;

        int keepserver;         /* Keep server alive */
        int filterhint;         /* Filter devices based on hint bits */
        int filterias;          /* Filter devices based on IAS entry */

        void *tx_msg;                /* Reusable transmit message */
        void *rx_msg;                /* Reusable receive message */

        obex_object_t   *object;        /* Current object being transfered */
        obex_event_t    eventcb;        /* Event-callback */

       obex_transport_t trans;         /* Transport being used */
        void *ctrans;
        void * userdata;                /* For user */
} obex;

int btobex_accept(obex *self)
{
        int addrlen = sizeof(struct sockaddr_rc);

        // First accept the connection and get the new client socket.
        self->fd = accept(self->serverfd, NULL, 0);//(struct sockaddr *) &self->trans.peer.rfcomm,
                          //&addrlen);

        if (self->fd < 0) {
                return -1;
        }

	self->trans.mtu = OBEX_DEFAULT_MTU;
        return 0;
}


#define OBEX_PUSH_HANDLE	10

volatile int finished = 0;
obex_t *handle = NULL;

void obex_event(obex_t *handle, obex_object_t *object, int mode, int event, int obex_cmd, int obex_rsp);

int main(int argc, char **argv)
{
	obex_object_t *object;

	handle = OBEX_Init(OBEX_TRANS_BLUETOOTH, obex_event, 0);

	if (argc == 1)
	{
		BtOBEX_ServerRegister(handle, NULL, OBEX_PUSH_HANDLE);
		printf("Waiting for connection...\n");
		btobex_accept(handle);

		while (!finished)
			OBEX_HandleInput(handle, 1);
	}
}
