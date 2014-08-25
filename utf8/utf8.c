
#include <stdio.h>
#include <termios.h>

int getcurline () {
	char buf[8];
	int curline;
	struct termios save,raw;
	tcgetattr(0,&save);
	cfmakeraw(&raw); tcsetattr(0,TCSANOW,&raw);
	if (isatty(fileno(stdin))) 
	{
		//write(1,"\033[6n\033[5n",8);
		write (1,"\033[6n\033[5n", 8);
		read (0 ,buf ,sizeof(buf));

		/* It doesn't work!!?
		sscanf(buf,"%d",curline);
		printf("\n\rCurrent Line: %d\n\r" , curline);
		*/
//printf ("\n\nBUF(%s)\n", buf+1);
//		printf("\n\rCurrent Line: %c%c\n\r" , buf[2] ,buf[3] );
	}
	tcsetattr(0,TCSANOW,&save);
	return curline;
}
main() {
	int a, b;
	a = getcurline ();
	write (1, "\xc3\x89\xc3\xa9", 4);
	b = getcurline ();
	printf ("\r%d %d = %d\n", a, b, b-a);
}
