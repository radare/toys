#import <UIKit/UIKit.h>

int main() {
	NSAutoreleasePool *innerPool = [[NSAutoreleasePool alloc] init];
	UIDevice *device = [UIDevice currentDevice];
	NSString *uuid = [device.uniqueIdentifier stringByReplacingOccurrencesOfString:@"-" withString:@""];
	printf ("%s\n", [uuid UTF8String]);
	return 0;
	[innerPool release];
}
