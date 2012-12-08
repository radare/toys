#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <sys/time.h>
#include <termios.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <sys/types.h>

int uppercase_mode = 0;
int mouse_mode = 1;

int mouse(int u, int x, int y)
{
	static int delta = 0;
	if (!mouse_mode)
		return;
	if (uppercase_mode) {
		if (y>3) printf("K\n");
		else if (y<-3) printf("J\n");
	} else {
		//printf("%d:   %d %d\n", u, x, y);
		if (y>2) printf("k\n");
		else if (y<-2) printf("j\n");
		if (x>2) printf("l\n");
		else if (x<-2) printf("h\n");
	}
	fflush(stdout);
}

// open /dev/tpy and select with stdin to direct write keys or enable/disable mouse
// use micey as a input
// micey -s 4 | radare -d ls
int set_icanon(int fd)
{
	struct termios tc;
	tcgetattr(fd, &tc);
	tc.c_iflag &= ~(BRKINT|PARMRK|ISTRIP|INLCR|IGNCR|ICRNL|IXON);
//	tc.c_lflag &= ~(ECHO|ECHONL|ICANON|ISIG|IEXTEN);
	tc.c_lflag &= ~(ICANON|ISIG|IEXTEN);
	tc.c_cflag &= ~(CSIZE|PARENB);
	tc.c_cflag |= CS8;
	tc.c_cc[VMIN] = 1;
	return tcsetattr(fd, TCSANOW, &tc);
}

int main(void)
{
	unsigned char ch;
	char buf[3];
	fd_set rfds;
	int tty = 0;
	int ret, tpy;

	set_icanon(0);
	//printf("pd\nV\n");
	tpy = open("/dev/input/mice", O_RDONLY);
	if (tpy == -1) {
		printf("Cannot open device\n");
		exit(1);
	}

	printf("b 100\npd\nV\n");
	fflush(stdout);
	while(1)
	{
		FD_ZERO(&rfds);
		FD_SET(0, &rfds);
		FD_SET(tpy, &rfds);
		ret = select(tpy+1, &rfds, NULL, NULL, NULL);
		if (ret == -1)
			break;
		if (ret) {
			if (FD_ISSET(tpy, &rfds)) {
				read(tpy, buf, 3);
				mouse(buf[0], buf[1], buf[2]);
			}
			if (FD_ISSET(0, &rfds)) {
				ret = read(0, &ch, 1);
				switch(ch) {
				case '^':
					mouse_mode ^=1;
					break;
				case '\'':
					uppercase_mode ^= 1;
					break;
				}
				if (ret>0) write(1, &ch, 1);
			}
		}
	}
	return 0;
}
