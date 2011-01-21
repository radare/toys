#include "llist.h"

struct llist *llist_new()
{
	struct llist *l;

	l=(struct llist *)malloc(sizeof(struct llist));
	l->next=0;
	l->ptr=0;

	return l;
}

void *llist_get(struct llist *l)
{
	return l->ptr;
}

void llist_put(struct llist *l,void *ptr)
{
	struct llist *last;

	if (l->ptr==0)
		last=l;
	else
		for (last=l;last->next!=0;last=last->next);

	last->ptr=ptr;
	last->next=(struct llist*)malloc(sizeof(struct llist));
	last->next->next=0;
	last->next->ptr=0;
}

/* returns 1 if llist is empty */
int llist_del(struct llist *l)
{
	if ( l->ptr==0 )
		return 1;

	if (l->next)
	{
		free(l->ptr);
		l->ptr=l->next->ptr;
		l->next=l->next->next;
	} else {
		/* remove last node */
		free(l->ptr);
		l->ptr=0;
	}
	return 0;
}

int llist_islast(struct llist *l)
{
	if ( l->ptr==0 )
		return 1;
	return 0;
}

struct llist *llist_kill(struct llist *l)
{
	while( ! llist_del(l) );
	free(l);
	return (struct llist *)0;
}

/*
main()
{
	struct llist *a;
	a=llist_new();
	llist_put(a,(void *)strdup("hehe"));
	llist_put(a,(void *)strdup("bubu"));
	llist_put(a,(void *)strdup("lolo"));
	while( ! llist_islast(a) )
	{
		printf("%s\n",llist_get(a));
		llist_del(a);
	}
	a=llist_kill(a);
}
*/


/* if ptr=0 nodes=0  *
 * if next=0 nodes=1 *
 * if ptrnext|ptr    */
