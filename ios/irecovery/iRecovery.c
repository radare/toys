/**
  * iRecovery - Utility for DFU, WTF and Recovery
  * Copyright (C) 2008 - 2009 westbaer, tom3q
  * 
  * This program is free software: you can redistribute it and/or modify
  * it under the terms of the GNU General Public License as published by
  * the Free Software Foundation, either version 3 of the License, or
  * (at your option) any later version.
  * 
  * This program is distributed in the hope that it will be useful,
  * but WITHOUT ANY WARRANTY; without even the implied warranty of
  * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  * GNU General Public License for more details.
  * 
  * You should have received a copy of the GNU General Public License
  * along with this program.  If not, see <http://www.gnu.org/licenses/>.
  **/

#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <usb.h>
#include <readline/readline.h>
#define DFU_MODE 0x1222
#define WTF_MODE 0x1227
#define RECOVERY_MODE 0x1281
#define TRANSFER_BUFFER_LEN 0x10000
#define COMMAND_BUFFER_LEN 512
#define AUTOCOMMAND_DUMPMEM 1

struct usb_dev_handle *globalDevPhone;

/*
 * A helper function dumping c bytes of a.
 */
void iHexDump(char *a, int c)
{
	int b;
	
	for(b=0;b<c;b++) {
		if(b%16==0&&b!=0)
			printf("\n");
		printf("%2.2X ",a[b]);
	}
	printf("\n");
}

/*
 * A helper function imitating GNU readline a bit...
 * (Places read line into *line)
 */
char *iReadLine(char *line)
{
	int c=0;
	char temp=0;

	scanf("%c",&temp);
	while(temp!='\n') {
		//printf("%2.2x\n",temp);
		line[c]=temp;
		c++;
		scanf("%c",&temp);
	}
	line[c]='\0';

	return line;
}

/*
 * A helper function initializing libusb and finding our iPhone/iPod which has given DeviceID
 */
struct usb_dev_handle *iUSBInit(int devid)
{
	struct usb_dev_handle *devPhone = 0;
	struct usb_device *dev;
	struct usb_bus *bus;

	usb_init();
	usb_find_busses();
	usb_find_devices();

	printf("Got USB\n");
	for(bus = usb_get_busses(); bus; bus = bus->next) {
		//printf("Found BUS\n");
		for(dev = bus->devices; dev; dev = dev->next) {
			//printf("\t%4.4X %4.4X\n", dev->descriptor.idVendor, dev->descriptor.idProduct);
			if(dev->descriptor.idVendor == 0x5AC && dev->descriptor.idProduct == devid) {
				// z0mg!!!! iPhone 4th Generation
//				printf("Found iPhone/iPod in DFU 2.0\n");
				devPhone = usb_open(dev);
			}
		}
	}

	return devPhone;
}

/*
 * A helper function closing the USB connection
 */
void iUSBDeInit(struct usb_dev_handle *devPhone)
{
	printf("Closing USB connection...\n");
	usb_close(devPhone);
}

/*
 * Internal command help
 */
void iHelp()
{
	printf("List of internal commands:\n");
	printf("/sendfile <file>\tsend <file> to the phone\n");
	printf("/dumpMem <args>\tdump memory\n");
	printf("/help\t\t\tshow this help\n");
	printf("/exit\t\t\texit the shell\n");
}
void iSendFile(char *filename);
void parseScript(char *filename);

/*
 * Internal command parser for -s mode
 */
void iParseCmd(char *cmd)
{
	char *command, *parameters;
	command = strtok(cmd, " ");
	parameters = strtok(NULL, " ");

	if(!strcmp("/help", command)) {
		iHelp();
	} else if(!strcmp("/sendfile", command)) {
		iSendFile(parameters);
	} else if(!strcmp("/script", command)) {
		parseScript(parameters);
	} else if(!strcmp("/exit", command) || strstr("/dumpMem", command)) {
		return;
	} else {
		printf("Unknown internal command. See /help\n");
	}
}

void finalizeDumpFile(char* dumpMemTmpFileName, char* dumpMemFileName) {
	char tmpbuf[512]; // will get each line of mdb output.
    	FILE * fTmp = fopen(dumpMemTmpFileName, "rb");
	FILE * fFinal = fopen(dumpMemFileName, "wb");
	unsigned int mdbByte;
	unsigned int nbBytes = 0;
	while (!feof(fTmp)) {
	    if (fgets(tmpbuf, 512, fTmp)==NULL) break;

	    	int count = strlen(tmpbuf);
		char* pDst = tmpbuf;
		while(pDst < tmpbuf + count) {
			if (nbBytes%17 != 0) {
				sscanf(pDst, "%x", &mdbByte);
				fputc(mdbByte, fFinal);
			}
			nbBytes++;
			while (*pDst!=' ' && pDst < tmpbuf + count) pDst++; // goto the next space
			while ((*pDst<'0' || *pDst>'9') && (*pDst<'a' || *pDst>'f') && pDst < tmpbuf + count) pDst++; // goto the next digit
        	}



	}
    	fclose(fFinal);
    	fclose(fTmp);
    	unlink(dumpMemTmpFileName);
}

void sendCommand(char *cmd) {
	struct usb_dev_handle *devPhone;
	char *sendbuf;
	devPhone = iUSBInit(RECOVERY_MODE);
	if(devPhone == 0) {
		printf("No iPhone/iPod found.\n");
		exit(EXIT_FAILURE);
	}
	sendbuf = malloc(160);
	int length = (int)(((strlen(cmd)-1)/0x10)+1)*0x10;
	memset(sendbuf, 0, length);
	memcpy(sendbuf, cmd, strlen(cmd));
	if(!usb_control_msg(devPhone, 0x40, 0, 0, 0, sendbuf, length, 1000)) {
		printf("[ ERROR ] %s", usb_strerror());
	}
	free(sendbuf);
	iUSBDeInit(devPhone);	
}

/*
 * Main function of -s mode
 */
	void iStartConsole(void)
	{
		struct usb_dev_handle *devPhone;
		int ret, length, skip_recv, firstresp;
		char *buf, *sendbuf, *tmpbuf, *cmd, *response;

		devPhone = iUSBInit(RECOVERY_MODE);
		globalDevPhone = devPhone;

		if(devPhone == 0) {
			printf("No iPhone/iPod found.\n");
			exit(EXIT_FAILURE);
		}

		if((ret = usb_set_configuration(devPhone, 1)) < 0)
			printf("Error %d when setting configuration\n", ret);

		if((ret = usb_claim_interface(devPhone, 1)) < 0)
			printf("Error %d when claiming interface\n", ret);

		if((ret = usb_set_altinterface(devPhone, 1)) < 0)
			printf("Error %d when setting altinterface\n", ret);

		buf = malloc(TRANSFER_BUFFER_LEN);
		tmpbuf = malloc(TRANSFER_BUFFER_LEN);
		sendbuf = malloc(COMMAND_BUFFER_LEN);
		cmd = malloc(COMMAND_BUFFER_LEN);

		skip_recv = 0;
		firstresp = 0;

		// >> variables related to /dumpMem command
	    	unsigned int dumpMemPtr, dumpMemAddr, dumpMemSize;
	    	FILE* dumpMemTmpFile;
	    	char dumpMemTmpFileName[COMMAND_BUFFER_LEN];
	    	char dumpMemFileName[COMMAND_BUFFER_LEN];
	    // <<

	    	int autoCommand = 0;
	    	do {
			if(!skip_recv) {
	            		memset(buf, 0, TRANSFER_BUFFER_LEN);
				ret = usb_bulk_read(devPhone, 0x81, buf, TRANSFER_BUFFER_LEN-1, 1000);

	            		if(ret > 0) {
					if (autoCommand == AUTOCOMMAND_DUMPMEM) {
						// removing all those \0 in the response
						char* pSrc = buf;
						char* pDst = tmpbuf;
						while (pSrc < buf + ret) {
							if (*pSrc != 0) {
								*(pDst++) = *pSrc;
							}
							pSrc++;
						}
						*pDst='\0'; // finishes the string

						fputs(tmpbuf, dumpMemTmpFile);
					} else {
						response = buf;
						while(response < buf + ret) {
							printf("%s", response);
							response += strlen(response) + 1;
						}
					}
				}

				if ( dumpMemPtr >= dumpMemAddr + dumpMemSize ) {
					// temporary dump finished. closing dump file.
					autoCommand = 0;
					fclose(dumpMemTmpFile);

					// reading the tmp dump file from the start and generates the final one
				    	finalizeDumpFile(dumpMemTmpFileName, dumpMemFileName);
				}
			} else {
				skip_recv = 0;
			}

			if (autoCommand==0) {
				if(firstresp == 1) {
					printf("] ", response);
				}
				cmd = readline(NULL);
				if(cmd && *cmd) {
					add_history(cmd);
				}

				if(firstresp == 0) {
					firstresp = 1;
				}
			} else if (autoCommand == AUTOCOMMAND_DUMPMEM) {
	   			memset(cmd, 0, COMMAND_BUFFER_LEN);
				int mdbSize = dumpMemAddr + dumpMemSize - dumpMemPtr;
	   			if (mdbSize > 0x40) mdbSize = 0x40;
		        	sprintf(cmd, "mdb 0x%08x 0x%08x\n", dumpMemPtr, mdbSize);
				// incrementing mdb pointer by 0x40
	   			dumpMemPtr += mdbSize;
			}

			if(cmd[0] == '/') {
				if (strstr(cmd, "/dumpMem")) {
					// want to dump memory.

					char command[COMMAND_BUFFER_LEN];
					unsigned int cmdParamAddr = 0, cmdParamSize = 0;
					sscanf(cmd, "%s %s 0x%x 0x%x", command, dumpMemFileName, &cmdParamAddr, &cmdParamSize);

	                if (strlen(dumpMemFileName)>0 && cmdParamAddr > 0 && cmdParamSize > 0) {
	                    autoCommand = AUTOCOMMAND_DUMPMEM;
						strcpy(dumpMemTmpFileName, dumpMemFileName);
						strcat(dumpMemTmpFileName, ".tmp");
						dumpMemTmpFile = fopen(dumpMemTmpFileName, "wb");
						dumpMemAddr = cmdParamAddr;
						dumpMemSize = cmdParamSize;
						dumpMemPtr = dumpMemAddr;
					} else {
						printf("syntax: /dumpMem <filename> 0x<addr> 0x<len>\n");
					}
				} else {
	                iParseCmd(cmd);
				}
				skip_recv = 1;
			} else {
				length = (int)(((strlen(cmd)-1)/0x10)+1)*0x10;
				memset(sendbuf, 0, length);
				memcpy(sendbuf, cmd, strlen(cmd));
				if(!usb_control_msg(devPhone, 0x40, 0, 0, 0, sendbuf, length, 1000)) {
					printf("[ ERROR ] %s", usb_strerror());
				}
			}


		} while(strcmp("/exit", cmd) != 0);

		usb_release_interface(devPhone, 0);
		free(buf);
		free(tmpbuf);
		free(sendbuf);
		free(cmd);
		iUSBDeInit(devPhone);
}

void parseScript(char *filename) { 
	FILE *file;
	char cmdbuf[100];
	int length, ret;
	char *sendbuf, *buf, *response;
	sendbuf = malloc(160);
	buf = malloc(0x10001);
	file = fopen(filename, "rb");
	if(file == NULL) {
		printf("File %s not found.\n", filename);
	} else {
		while (!feof(file)) {
			memset(buf, 0, TRANSFER_BUFFER_LEN);
			ret = usb_bulk_read(globalDevPhone, 0x81, buf, TRANSFER_BUFFER_LEN-1, 1000);

            		if(ret > 0) {
				response = buf;
				while(response < buf + ret) {
					printf("%s", response);
					response += strlen(response) + 1;
				}
			}
			
			fgets(cmdbuf, 99, file);
			printf("send: %s", cmdbuf);
			length = (int)(((strlen(cmdbuf)-1)/0x10)+1)*0x10;
			memset(sendbuf, 0, length);
			memcpy(sendbuf, cmdbuf, strlen(cmdbuf));
			if(!usb_control_msg(globalDevPhone, 0x40, 0, 0, 0, sendbuf, length, 1000)) {
				printf("[ ERROR ] %s", usb_strerror());
			}
		}
	}
	
	fclose(file);
}

/*
 * Main function of -f mode
 */
void iSendFile(char *filename)
{
	struct usb_dev_handle *devPhone;
	FILE *file;
	int packets, len, last, i, a, c, sl;
	char *fbuf, buf[6];
	
	if(!filename)
		return;

	file = fopen(filename, "rb");
	if(file == NULL) {
		printf("File %s not found.\n", filename);
		exit(EXIT_FAILURE);
	}
	fseek(file, 0, 0);
	fclose(file);

	devPhone = iUSBInit(WTF_MODE);
	if(!devPhone) {
		devPhone = iUSBInit(RECOVERY_MODE);
		if(devPhone)
			printf("Found iPhone/iPod in Recovery mode\n");
	} else {
		printf("Found iPhone/iPod in DFU/WTF mode\n");
	}

	if(!devPhone) {
		printf("No iPhone/iPod found.\n");
		exit(EXIT_FAILURE);
	}

	if(usb_set_configuration(devPhone,	1))
		printf("Error setting configuration\n");

	printf("\n");

	file = fopen(filename, "rb");
	fseek(file, 0, SEEK_END);
	len = ftell(file);
	fseek(file, 0, 0);

	packets = len / 0x800;
	if(len % 0x800)
		packets++;
	last = len % 0x800;

	printf("Loaded image file (len: 0x%x, packets: %d, last: 0x%x).\n", len, packets, last);

	fbuf = malloc(packets * 0x800);
	if(!last)
		last = 0x800;
	fread(fbuf, 1, len, file);
	fclose(file);

	printf("Sending 0x%x bytes\n", len);

	for(i=0, a=0, c=0; i<packets; i++, a+=0x800, c++) {
		sl = 0x800;

		if(i == packets-1)
			sl = last;

		printf("Sending 0x%x bytes in packet %d... ", sl, c);

		if(usb_control_msg(devPhone, 0x21, 1, c, 0, &fbuf[a], sl, 1000)) {
			printf(" OK\n");
		} else{
			printf(" x\n");
		}

		if(usb_control_msg(devPhone, 0xA1, 3, 0, 0, buf, 6, 1000) != 6){
			printf("Error receiving status!\n");
		} else {
			iHexDump(buf, 6);
			if(buf[4]!=5)
				printf("Status error!\n");
		}
	}

	printf("Successfully uploaded file!\nExecuting it...\n");	

	usb_control_msg(devPhone, 0x21, 1, c, 0, fbuf, 0, 1000);

	for(i=6; i<=8; i++) {
		if(usb_control_msg(devPhone, 0xA1, 3, 0, 0, buf, 6, 1000) != 6){
			printf("Error receiving status!\n");
		} else {
			iHexDump(buf, 6);
			if(buf[4]!=i)
				printf("Status error!\n");
		}
	}

	free(fbuf);
	iUSBDeInit(devPhone);
}

/*
 * Shows the Arguments of the application.
 */
int iShowUsage(void)
{
		printf("./iRecovery [args]\n");
		printf("\t-f <file>\t\tupload file in DFU, WTF and Recovery modes\n");
		printf("\t-c \"command\"\t\tsend a single command in recovery mode\n");
		printf("\t-s\t\t\tstarts a shell in Recovery mode\n\n");
}

/*
 * Main function of the application
 */
int main(int argc, char *argv[])
{
	printf("iRecovery - Recovery Utility\n");
	printf("by westbaer\nThanks to pod2g and tom3q\n\n");
	if(argc < 2) {
		iShowUsage();
		exit(EXIT_FAILURE);
	}

	if(argv[1][0] != '-') {
		iShowUsage();
		exit(EXIT_FAILURE);
	}
	
	if(strcmp(argv[1], "-f") == 0) {
		if(argc < 3) {
			// error when 3rd arg for file upload is not set
			printf("No valid file set.\n");
			exit(EXIT_FAILURE);
		} 
		iSendFile(argv[2]);
	} else if(strcmp(argv[1], "-s") == 0) {
		iStartConsole();
	} else if(strcmp(argv[1], "-c") == 0) {
		sendCommand(argv[2]);
	}
	
	return 0;
}
