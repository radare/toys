#include <stdio.h>
#define CPUID_GETVENDOR 0

int pr(int v) {
	printf ("%c", (v&0xff));
	printf ("%c", (v>>8&0xff));
	printf ("%c", (v>>16&0xff));
	printf ("%c", (v>>24&0xff));
}

main() {
	char str[32];
	int a,b,c,d;
	asm("cpuid"
		:"=a"(a),"=b"(b),"=c"(c),"=d"(d) /* out */
		:"a"(0) /* in*/
		);
printf ("ModelString: ");
	//--//
	pr(b);
	pr(d);
	pr(c);
	pr(a);

printf ("\nL2 cache details: \n");
	// L1 cache and TLB identifier
	asm ("cpuid"
		:"=a"(a),"=b"(b),"=c"(c),"=d"(d) /* out */
		:"a"(0x80000006) /* in*/
		);
	printf ("C=%x\n", c);
printf ("FamilyModelSteps:\n");
	asm ("cpuid"
		:"=a"(a),"=b"(b),"=c"(c),"=d"(d) /* out */
		:"a"(1) /* in*/
		);
	printf ("  A=%x\n", a);
	printf ("  B=%x\n", b);
	printf ("  C=%x\n", c);
	printf ("  D=%x\n", d);
printf ("LargestAddressWidth\n");
	asm ("cpuid"
		:"=a"(a),"=b"(b),"=c"(c),"=d"(d) /* out */
		:"a"(0x80000008) /* in*/
		);
	printf ("  A=%x\n", a);
}
