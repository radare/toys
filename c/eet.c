/* GPLv3 -- 2009 -- nibble /at/ develsec.org */

#include <stdio.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>

int main(int argc, char **argv)
{
	fd_set rfds;
	struct timeval tv;
	char buf[1024];
	int nfds, fds[16], last, i, ret;

	for(nfds = 1, last = 0, fds[0] = 0; nfds < argc && nfds < 16; nfds++) {
		if ((fds[nfds] = open(argv[nfds], O_RDONLY|O_NONBLOCK)) == -1) {
			fprintf(stderr, "Cannot open '%s'\n", argv[nfds]);
			return 1;
		}
		if (fds[nfds] > last)
			last = fds[nfds];
	}

	tv.tv_sec = 1;
	tv.tv_usec = 0;
	do {
		FD_ZERO(&rfds);
		for(i = 0 ; i < nfds; i++)
			FD_SET(fds[i], &rfds);
		if ((ret = select(last + 1, &rfds, NULL, NULL, &tv)) > 0)
			for(i = 0; i < nfds; i++)
				if (FD_ISSET(fds[i], &rfds)) {
					memset(buf, '\0', 1024);
					read(fds[i], buf, 1023);
					printf("%s", buf);
					FD_CLR(fds[i], &rfds);
				}
	} while(ret != -1);

	return 0;
}
