/*

   chroot shell loader

   author : pancake@youterm.com

*/

#define MY_UID    1111
#define MY_GID    2222
#define MY_CHROOT "/home/jails"
#define MY_HOME   "/home"
#define MY_PROMPT "\\w> "
#define MY_SHELL  "/bin/sh"
#define MY_SHNAME "[chroot-shell]"

int main(int argc, char **argv)
{
//	char *HOME=(char *)getenv("HOME");
	char *HOME = (char *)MY_HOME;
	
	if ( getuid() != MY_UID ) {
		printf("Invalid UID\n");
		return 1;
	}

	if ( setreuid(0, 0) ) {
		perror("Got Root?");
		return 2;
	}
	
	/* chroot */
	chdir(MY_CHROOT);
	chroot(".");
	
	/* chuid */
	setregid(MY_GID, MY_GID);
	setreuid(MY_UID, MY_UID);

	/* check */
	if ( access("/bin", 0) ) {
		printf("***\nHome is damaged or not mounted. Exiting. ***\n");
		return 3;
	} 

	/* setenv */
	setenv("PS1", PROMPT); 
	setenv("HOME", HOME, 1);

	if (HOME) chdir(HOME);
	else chdir("/");

	execl(MY_SHELL, MY_SHNAME, 0);

	return 0;
}
