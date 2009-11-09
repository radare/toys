/*
 * libwipe
 *
 * NOTE: This is an incomplete version of libwipe. It's just for testing
 *       purposes, so, it works, but it just zeroes the file, this is not
 *       a secure deletion method, and it just wraps the unlink() syscall.
 *
 * TODO: Implement better wiping algorithms
 *       Handle ^C :) sigign? or just warn 2 times? or prompt?
 *       Use mmap instead of open/lseek/write/close
 *       Wrap truncate(2) and ftruncate(2)
 *       Wrap rmdir(?)
 *       Make use of the errno
 *       Use environ for runtime configuration
 *         LIBWIPE_METHOD
 *         LIBWIPE_VERBOSE
 *         LIBWIPE_DISABLE
 *         ...
 *
 * BUILD: gcc -shared -ldl libwipe.c -o libwipe.so
 *
 * INSTALL: cp libwipe.so /lib && echo /lib/libwipe.so >> /etc/ld.so.preload
 *
 * author: pancake <pancake@youterm.com>
 * description: wipe as a library
 * 
 */

#define _GNU_SOURCE
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <dlfcn.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>

int * (*__unlink)(const char *pathname);
static int verbose = 1;

/*
 * Library initialization
 */
static void _libwipe_init() __attribute__ ((constructor));
static void _libwipe_init()
{   
	char *ptr = getenv("LIBWIPE_VERBOSE");
	__unlink = dlsym(RTLD_NEXT, "unlink");

	if (__unlink == NULL) {
		printf("Library initialization failed.\n");
		exit(1);
	}
  
	if (ptr) verbose = atoi(ptr);
}

static void _libwipe_fini() __attribute__ ((destructor));
static void _libwipe_fini()
{
	/* do something here */
}

static void randset(void *buf, size_t size)
{
	int fd = open("/dev/urandom",O_RDONLY);
	if (fd != -1) {
		read(fd, buf, size);
		close(fd);
	}
}

static int do_wipe(const char *pathname, blksize_t size)
{
  off_t offset;
  char *buf;
  register int i;
  int fd;

  buf = (char *)malloc(size);
  randset((void *)buf, (size_t)size);
  //memset((void *)buf, '\0', (size_t)size);

  /* todo: use mmap */
  fd = open(pathname, O_WRONLY);
  if (fd>=0) {
	offset = lseek(fd, 0, SEEK_END);
	if (offset<1) {
		free(buf);
		return 0;
	}

	if (verbose)
	printf("[+] Wiping %s (%ld bytes).\n", pathname, offset);
	lseek(fd, 0, SEEK_SET);
	for(i=0;i<offset;i+=size) {
		write(fd, buf, size);
	}
/*
	for(offset>>=2;offset>0;offset-=2) {
		write(fd, "\0\0", 2);
	}
*/
	close(fd);
	sync();
  } else {
	if (verbose)
	printf("[E] Cannot open '%s' for writing.\n", pathname);
	// only for SECURE mode,
		free(buf);
return -1;
  }

		free(buf);
	return 0;

}

int unlink( const char *pathname )
{
	struct stat st;

	lstat(pathname, &st);
//printf("%x %d %d\n", st.st_mode, S_ISLNK(st.st_mode), S_ISREG(st.st_mode));
	if (S_ISREG(st.st_mode)==1) {
		if (do_wipe(pathname, st.st_blksize))
			return -1;
	}

	return (int)(__unlink( pathname ));
}
