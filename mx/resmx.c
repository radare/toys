#include "resmx.h"
#include "llist.h"
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <netinet/in.h>
#include <sys/types.h>
#include <arpa/nameser.h>
#include <resolv.h>
#define BIND_4_COMPAT

int resmx_iserror(struct llist* l)
{
	if ((int)l<RESMX_ERROR)
		return 1;
	return 0;
}

char* resmx_errors[]=
{
	"not found",
	"expand",
	"dns error",
	"no error"
};

char* resmx_tostring(struct llist* l)
{
	if ( ((int)l>0) && ((int)l<RESMX_ERROR) )
	{
		return resmx_errors[(int)l];
	}
	return resmx_errors[RESMX_NOERROR];
}

struct llist* resmx_get(char* domain)
{
	char host[NS_MAXDNAME+1],
		last[NS_MAXDNAME+1];
	typedef union {
	HEADER head;
		char buf[PACKETSZ];
	} pkt_t;
	pkt_t *pkt;
	unsigned char buf[PACKETSZ];
	unsigned char *rrptr;
	int querylen,len,n;
	int exprc;
	int rrtype,antrrtype;
	int rrpayloadsz;
	struct llist* res;

	res=llist_new();

	querylen=res_querydomain(
		domain,"",
		C_IN,T_MX,
		(unsigned char*)&buf,PACKETSZ);

	pkt=(pkt_t *)buf;

	if (ntohs(pkt->head.rcode) == NOERROR)
	{
		n=ntohs(pkt->head.ancount);
		if (n==0)
		{
			llist_kill(res);
			return (struct llist*)RESMX_NOTFOUND;
		}

		/* expand DNS query */
		len=dn_expand(
			buf,
			buf+querylen, buf+sizeof(HEADER),
			host,    sizeof(host));

		if (len<0)
		{
			llist_kill(res);
			return (struct llist*)RESMX_EXPAND;
		}

		rrptr=buf+sizeof(HEADER)+4+len;

		while( rrptr < buf+querylen )
		{
			/* expand NAME resolved */
			exprc=dn_expand(buf,buf+querylen,rrptr,host,sizeof(host));
			if (exprc<0) 
			{
				llist_kill(res);
				return (struct llist*)RESMX_EXPAND;
			}

			rrptr+=exprc;
			rrtype=(rrptr[0]<<8|rrptr[1]);
			rrpayloadsz=(rrptr[8]<<8|rrptr[9]);
			rrptr+=10; 

			switch(rrtype)
			{	
			/* TODO support for IPv6 */
			/*	case T_AAAA: */
			case T_A:
				if (strcmp(host,last))
				{
					llist_put(res,strdup(host));
					strncpy(last,host,NS_MAXDNAME);
					n--;
					if (n==0) querylen=0; /* break loop */
				}
				break;
			}

			antrrtype=rrtype;
			rrptr+=rrpayloadsz; //+10; /* +10 ? */
		 }
	} else {
		llist_kill(res);
		return (struct llist*)RESMX_DNSERROR;
	}

	return res;
}

int main(int argc,char *argv[])
{
	struct llist *l;
	char *x;
	char *ptr;

	if (argc!=2) {
		printf("mx[list] [host]\n");
		return 0;
	}
	ptr = argv[1];
	x = strchr(argv[1], '@');
	if (x)
		ptr = x+1;
	l=resmx_get(ptr);

	if (resmx_iserror(l))
	{
		printf("%s\n",resmx_tostring(l));
	}

	while ( !llist_islast(l) )
	{
	#ifdef MX
		printf("%s\n",(char *)llist_get(l) );
		return 0;
	#endif
		printf("%s\n",(char *)llist_get(l) );

		llist_del(l);
	}

	llist_kill(l);

	return 0;
}
