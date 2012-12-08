/*
 * Copyright (C) 2006
 *       pancake <pancake@youterm.com>
 *
 * menush is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * menush is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with menush; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
 *
 */

#define HAVE_LIB_READLINE 1

#include <termios.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>

#if HAVE_LIB_READLINE
#include <readline/history.h>
#include <readline/readline.h>

char **rad_autocompletion(const char *text, int start, int end)
{
        char **matches = (char **)NULL;
	// TODO : support for argv
	return matches;
}
#endif

static struct termios tio_old, tio_new;

void terminal_set_raw(int b)
{
        if (b) {
                tcgetattr(0, &tio_old);
                memcpy ((char *)&tio_new, (char *)&tio_old, sizeof(struct termios));
                tio_new.c_iflag &= ~(BRKINT|PARMRK|ISTRIP|INLCR|IGNCR|ICRNL|IXON);
                tio_new.c_lflag &= ~(ECHO|ECHONL|ICANON|ISIG|IEXTEN);
                tio_new.c_cflag &= ~(CSIZE|PARENB);
                tio_new.c_cflag |= CS8;
                tio_new.c_cc[VMIN]=1; // Solaris stuff hehe
                tcsetattr(0, TCSANOW, &tio_new);
                fflush(stdout);
                return;
        }

        tcsetattr(0, TCSANOW, &tio_old);
	fflush(stdout);
}

int main(int argc, char **argv)
{
	unsigned char buf[10];
	memset(buf,0,10);

	if (argc==1) {
		terminal_set_raw(1);
		read(0, buf, 1);
		switch(buf[0]) {
		case 127:
			printf("backspace\n");
			break;
		case 27:
			read(0, buf, 5);
			printf("esc-%02x-%02x-%02x-%02x\n", buf[0],buf[1],buf[2],buf[3]);
			break;
		case 194:
		case 197:
		case 195:
		case 226:
			read(0, buf, 2);
			printf("unicode-%02x-%02x\n", buf[0],buf[1]);
			break;
		case 0:
			printf("control-space\n");
			break;
		case 0x20:
			printf("space\n");
			break;
		case 13:
			printf("intro\n");
			break;
		case 9:
			printf("tab\n");
			break;
		default:
			printf("%c\n", buf[0]);
			break;
		}
		terminal_set_raw(0);
	} else {
		if (!strcmp(argv[1],"-h")) {
			printf("Usage: eread [-r] | [[-d][-m] [item1] [item2] [...]]\n");
			printf(" -r    readline input.\n");
			printf(" -d    dmenu emulation.\n");
			printf(" -m    menu mode.\n");
		} else
		if (!strcmp(argv[1],"-m")) {
			int i,running=1,option=0;
			terminal_set_raw(1);
			do {
				fprintf(stderr, "\e[2J\e[0;0f");
				for (i=2; i<argc;i++) {
					fprintf(stderr," %c %s\n", (option+2==i)?'*':' ', argv[i]);
				}
				fflush(stderr);
				read(0,buf,1);
				if (buf[0]==27) {
					read(0, buf, 5);
					switch(buf[1]) {
					case 0x41: if (option>0) option--; else option=argc-3; break;
					case 0x42: if (option+3<argc) option++; else option=0; break;
					case 0x43: running=0; break;
					case 0x44: buf[0]='q'; running=0; break;
					}
				} else {
					switch(buf[0]) {
					case 'q':
					case 'Q':
					case ' ':
					case '\r':
					case '\n':
					case 'l':
					case 'h':
						 running=0; break;
			
					case 'k': if (option>0) option--; else option=argc-3; break;
					case 'j': if (option+3<argc) option++; else option=0; break;
					}
				}
			} while(running);

			terminal_set_raw(0);

			switch(buf[0]) {
			case 'h':
			case 'q':
				printf("quit");
				break;
			case 'Q':
				break;
			default:
				printf("%s\n", argv[option+2]);
				break;
			}
		} else
		if (!strcmp(argv[1],"-d")) {
			char line[1024];
			int line_len = 0;
			int idx = 0, off = 0;
#if HAVE_LIB_READLINE
			rl_initialize();
#endif
			terminal_set_raw(1);
			while(1) {
				int i, len = 0;
				int columns = 80;
#if HAVE_LIB_READLINE
				rl_reset_screen_size();
				rl_get_screen_size(NULL, &columns);
#endif

				for(i=2;i<argc;i++) {
					if (line_len==0||!strncmp(argv[i], line, line_len)) {
						len+=strlen(argv[i])+1;
						if (len+line_len+4 >= columns) break;
						fprintf(stderr,"%s ", argv[i]);
					}
				}
				fflush(stderr);

				line[line_len]='\0';
				read(0, buf, 1);

				fprintf(stderr,"\r");
				for(i=0;i<columns;i++) fprintf(stderr," ");
				fprintf(stderr,"\r");

				switch(buf[0]) {
				case 127:
					line_len--;
					if (line_len<0) line_len=0;
					line[line_len]='\0';
					break;
				case 9:
					for(i=2;i<argc;i++) {
						if (!strncmp(argv[i], line, line_len)) {
							strcpy(line, argv[i]);
							line_len = strlen(line);
							break;
						}
					}
					break;
				case 13:
					for(i=2;i<argc;i++) {
						if (line_len==0 || !strncmp(argv[i], line, line_len)) {
							for(i=0;i<columns;i++) fprintf(stderr," ");
							fprintf(stderr,"\r");
							printf("%s\n", line);
							terminal_set_raw(0);
							exit(0);
						}
					}
					
					printf("%s\n", line);
					terminal_set_raw(0);
					exit(0);
					break;
				default:
					line[line_len]=buf[0];
					line_len++;
					if (line_len>1000)
						line_len--;
					line[line_len]='\0';
				}
				fprintf(stderr,"\r%s  ", line);

			}
			terminal_set_raw(0);
		} else
		if (!strcmp(argv[1],"-r")) {
			/* readline */
#if HAVE_LIB_READLINE
			rl_outstream = stderr;
			rl_initialize();
			rl_set_prompt("");
			rl_redisplay();
			rl_attempted_completion_function = rad_autocompletion;
			printf("%s\n", readline(""));
#else
			printf("Sorry. compiled without readline support.\n");
			return(1);
#endif
		}
	}
	return(0);
}
