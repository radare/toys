#ifndef _INCLUDE_LLIST_H_
#define _INCLUDE_LLIST_H_

#include <stdlib.h>

struct llist
{
	void *ptr;
	struct llist *next;
};

struct llist* llist_new();

void* llist_get(struct llist* );

void llist_put(struct llist*,void*);

int llist_del(struct llist*);

int llist_islast(struct llist*);

struct llist *llist_kill(struct llist*);

#endif
