/* author: pancake<nopcode.org> */
#include <u.h>
#include <libc.h>

static vlong bsize = 0;
static char *buf;
#define LINES 4096

void
tac()
{
	int i, j;
	char *ptr, **nls;
	nls = malloc(LINES*sizeof(nls));
	for(i=1, ptr=buf; ptr;) {
		assert(nls != NULL);
		for(j=0; j<LINES && (ptr=strchr(ptr+1, '\n')); j++)
			nls[i++] = ptr+1;
		nls = realloc(nls, (i+LINES)*sizeof(nls));
	}
	*nls = buf;
	while(i--)
		write(1, nls[i], nls[i+1]-nls[i]);
	free(nls);
}

void
load(int f)
{
	vlong nsize, size = seek(f, 0, 2);
	if (size>0) {
		nsize = bsize + size;
		buf = realloc(buf, nsize);
		seek(f, 0, 0);
		read(f, buf+bsize, size);
		bsize = nsize;
	} else
	while ((size = read(f, buf+bsize, LINES))>0)
		bsize+=size;
}

void
main(int argc, char *argv[])
{
	int i, f;
	buf = malloc(1);
	assert(buf != NULL);
	if (argc == 1)
		load(0);
	else for(i=1; i<argc; i++){
		f = open(argv[i], OREAD);
		if(f >= 0){
			load(f);
			close(f);
		}else sysfatal("can't open %s: %r", argv[i]);
	}
	tac();
	free(buf);
	exits(0);
}
