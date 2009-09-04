#!/usr/bin/perl -w
# author: pancake
# license: gplv3
use strict;
use warnings;

my $q=$ARGV[0]||"";
my $o=$ARGV[1]||"";

while(1) {
	print "Category: $q";
	chomp($q=<STDIN>) unless ($q);
	next if ($q eq "");
	print "\n";

	while(1) {
		#my @urls=split(/\n/, `curl -s -d "s=$q" http://shoutcast.com/directory/index.phtml | perl -ne 'if (/pls/){/href="([^"]*)/;print "\$1\n";}'`);
		my @urls=split(/\n/, `curl -s -d "s=$q" http://shoutcast.com/directory/index.phtml | perl -ne 'if (/_scurl/){/_scurl" href="[^>]*([^<]*)/;print; "\$1\n"}if (/pls/){/href="([^"]*)/;print "\$1\n";}'`);

		my $n = 0;
		for(my $i=1;$i<@urls;$i+=2) {
			if ($urls[$i]=~/"_scurl"/) {
				$urls[$i]=~/_scurl"[^>]*(.*)<\/a>/;
				$urls[$i]=$1;
				$urls[$i]=~s/^.//;
			}
			printf " %03d  ".$urls[$i]."\n", $n;
			$n++;
		}
		print " q    quit\n";
		print "Choose: ";
		my $c = "";
		if ($o ne "") {
			$c = $o;
		} else {
			chomp($c=<STDIN>);
			last if ($c eq "q");
		}
		my $url = $urls[(int $c)*2];

		@urls=split(/\n/,`curl -s 'http://shoutcast.com/$url' | perl -ne 'if (/File/){/=(.*)\$/;print "\$1\n";}'`);
		my $mplayer="mplayer ";
		for(my $i=0;$i<@urls;$i+=2) {
			$mplayer.=$urls[$i*2]." ";
		}
		print "\n\nLaunching $mplayer\n\n";
		system($mplayer);
		exit() if ($o ne "") 
	}
	$q="";
}
