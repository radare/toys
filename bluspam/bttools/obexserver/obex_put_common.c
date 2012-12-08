/*********************************************************************
 *                
 * Filename:      obex_common.c
 * Version:       0.4
 * Description:   Utility-functions to act as a PUT server and client
 * Status:        Experimental.
 * Author:        Pontus Fuchs <pontus.fuchs@tactel.se>
 * Created at:    Sat Nov 20 10:54:14 1999
 * Modified at:   Sun Aug 13 01:54:05 PM CEST 2000
 * Modified by:   Pontus Fuchs <pontus.fuchs@tactel.se>
 * 
 *     Copyright (c) 1999, 2000 Pontus Fuchs, All Rights Reserved.
 *     
 *     This program is free software; you can redistribute it and/or 
 *     modify it under the terms of the GNU General Public License as 
 *     published by the Free Software Foundation; either version 2 of 
 *     the License, or (at your option) any later version.
 * 
 *     This program is distributed in the hope that it will be useful,
 *     but WITHOUT ANY WARRANTY; without even the implied warranty of
 *     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 *     GNU General Public License for more details.
 * 
 *     You should have received a copy of the GNU General Public License 
 *     along with this program; if not, write to the Free Software 
 *     Foundation, Inc., 59 Temple Place, Suite 330, Boston, 
 *     MA 02111-1307 USA
 *     
 ********************************************************************/

#include <stdio.h>
#include <stdlib.h>

#include <openobex/obex.h>
#include "obex_put_common.h"
#include "obex_io.h"

#define TRUE  1
#define FALSE 0

extern obex_t *handle;
extern volatile int finished;

volatile int last_rsp = OBEX_RSP_BAD_REQUEST;

/*
 * Function put_done()
 *
 *    Parse what we got from a PUT
 *
 */
void put_done(obex_object_t *object)
{
	obex_headerdata_t hv;
	uint8_t hi;
	int hlen;

	const uint8_t *body = NULL;
	int body_len = 0;
	char *name = NULL;
	char *namebuf = NULL;

	while(OBEX_ObjectGetNextHeader(handle, object, &hi, &hv, &hlen))	{
		switch(hi)	{
		case OBEX_HDR_BODY:
			body = hv.bs;
			body_len = hlen;
			break;
		case OBEX_HDR_NAME:
			if( (namebuf = malloc(hlen / 2)))	{
				OBEX_UnicodeToChar(namebuf, hv.bs, hlen);
				name = namebuf;
			}
			break;

		case OBEX_HDR_LENGTH:
			printf("HEADER_LENGTH = %d\n", hv.bq4);
			break;

		case HEADER_CREATOR_ID:
			printf("CREATORID = %#x\n", hv.bq4);
			break;
		
		default:
			printf(__FUNCTION__ "() Skipped header %02x\n", hi);
		}
	}
	if(!body)	{
		printf("Got a PUT without a body\n");
		return;
	}
	if(!name)	{
		printf("Got a PUT without a name. Setting name to %s\n", name);
		name = "OBEX_PUT_Unknown_object";

	}
	safe_save_file(name, body, body_len);
	free(namebuf);
}


/*
 * Function server_indication()
 *
 * Called when a request is about to come or has come.
 *
 */
void server_request(obex_object_t *object, int event, int cmd)
{
	switch(cmd)	{
	case OBEX_CMD_SETPATH:
		printf("Received SETPATH command\n");
		OBEX_ObjectSetRsp(object, OBEX_RSP_CONTINUE, OBEX_RSP_SUCCESS);
		break;
	case OBEX_CMD_PUT:
		OBEX_ObjectSetRsp(object, OBEX_RSP_CONTINUE, OBEX_RSP_SUCCESS);
		put_done(object);
		break;
	case OBEX_CMD_CONNECT:
		OBEX_ObjectSetRsp(object, OBEX_RSP_SUCCESS, OBEX_RSP_SUCCESS);
		break;
	case OBEX_CMD_DISCONNECT:
		OBEX_ObjectSetRsp(object, OBEX_RSP_SUCCESS, OBEX_RSP_SUCCESS);
		break;
	default:
		printf(__FUNCTION__ "() Denied %02x request\n", cmd);
		OBEX_ObjectSetRsp(object, OBEX_RSP_NOT_IMPLEMENTED, OBEX_RSP_NOT_IMPLEMENTED);
		break;
	}
	return;
}

/*
 * Function client_done_indication()
 *
 * Called when a server-operation has finished
 *
 */
void server_done(obex_object_t *object, int obex_cmd)
{
	/* Quit if DISCONNECT has finished */
	if(obex_cmd == OBEX_CMD_DISCONNECT)
		finished = 1;
}


/*
 * Function client_done()
 *
 * Called when a client-operation has finished
 *
 */
void client_done(obex_object_t *object, int obex_cmd, int obex_rsp)
{
	last_rsp = obex_rsp;
	finished = TRUE;
}

/*
 * Function obex_event ()
 *
 *    Called by the obex-layer when some event occurs.
 *
 */
void obex_event(obex_t *handle, obex_object_t *object, int mode, int event, int obex_cmd, int obex_rsp)
{
	switch (event)	{
	case OBEX_EV_PROGRESS:
		printf(".");
		break;
	case OBEX_EV_REQDONE:
		printf("\n");
		/* Comes when a command has finished. */
		if(mode == OBEX_CLIENT)
			client_done(object, obex_cmd, obex_rsp);
		else
			server_done(object, obex_cmd);
		break;
	case OBEX_EV_REQHINT:
		/* Comes BEFORE the lib parses anything. */
		switch(obex_cmd) {
		case OBEX_CMD_PUT:
		case OBEX_CMD_CONNECT:
		case OBEX_CMD_DISCONNECT:
			OBEX_ObjectSetRsp(object, OBEX_RSP_CONTINUE, OBEX_RSP_SUCCESS);
			break;
		default:
			OBEX_ObjectSetRsp(object, OBEX_RSP_NOT_IMPLEMENTED, OBEX_RSP_NOT_IMPLEMENTED);
			break;
		}
		break;
	case OBEX_EV_REQ:
		/* Comes when a server-request has been received. */
		server_request(object, event, obex_cmd);
		break;
	case OBEX_EV_LINKERR:
		printf("Link broken (this does not have to be an error)!\n");
		finished = 1;
		break;
	default:
		printf("Unknown event!\n");
		break;
	}
}

/*
 * Function wait_for_rsp()
 *
 *    Wait for a request to finish!
 *
 * Timeout set to 10s. Should be more than good enough for most transport.
 */
int wait_for_rsp()
{
	int ret;

	while(!finished) {
		//printf("wait_for_rsp()\n");
		ret = OBEX_HandleInput(handle, 10);
		if (ret < 0)
			return ret;
	}
	return last_rsp;
}

/*
 * Function do_sync_request()
 *
 *    Execute an OBEX-request synchronously.
 *
 */
int do_sync_request(obex_t *handle, obex_object_t *object, int async)
{
	int ret;
	OBEX_Request(handle, object);
	ret = wait_for_rsp();
	finished = FALSE;
	return ret;
}
