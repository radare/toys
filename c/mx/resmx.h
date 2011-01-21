#ifndef _INCLUDE_RESMX_H_
#define _INCLUDE_RESMX_H_

#include "llist.h"

enum {
	RESMX_NOTFOUND,
	RESMX_EXPAND,
	RESMX_DNSERROR,
	RESMX_NOERROR,
	RESMX_ERROR
};

int resmx_iserror(struct llist *l);

char *resmx_tostring(struct llist *l);

struct llist* resmx_get(char *domain);

#endif
