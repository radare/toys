#!/usr/bin/perl
#
# dpanel - keyboard friendly panel for X using dmenu
#
# author: pancake <pancake at youterm dot com>
#
# To get dmenu:
#  http://www.suckless.org/wiki/tools/xlib
#
# Put your own configuration in ~/.dpanel.conf. for example:
#
#    push @commands, "ssh-router";
#    $bare = "$xterm -e 'ssh root\@192.168.0.1'";
#    $xlock = "xset dpms force off && slock";
#
# The $agenda format is something like this: (in tsv format (tab separated values))
#
#     mail	pancake	my@mail.com
#     alias	pop	pancake
#     mail	dwm	dwm-mailing@suckless
#     alias	dwm-list dwm
#
#

## User Configuration ##

my $home       = $ENV{"HOME"};
my $xterm      = "uxterm -bg black -fg gray -fn 10x20";
my $im         = "gaim";
my $irc        = "$xterm -e 'irssi -c irc.freenode.net'";
my $irc2       = "$xterm -e 'irssi -c libers.irc-hispano.org'";
my $ssh        = "$xterm -e 'ssh pancake\@news.nopcode.org'";
my $agenda     = "$home/.agenda";
my $mail       = "sylpheed";
my $browser    = "firefox";
my $scratchbox = "$xterm -e 'sudo /scratchbox/sbin/sbox_ctl start && /scratchbox/login'";
my $fetchmail  = "sylpheed --receive";
my $xlock      = "sleep 1 && xset dpms force off";
my $halt       = "$xterm -e 'sudo halt'";
my $xkill      = "xkill";
my $notes      = "$xterm -e 'vim $home/crypto/links'";
my $mixer      = "$xterm -e 'aumix'";
my $music      = "$xterm -e 'cd $home/mp3/8bc/ && perl play.pl'"; #mplayer $home/mp3/*/* $home/mp3/*/*/*";
my $screenshot = "scrot $home/shot.png";
my $browser_history = "$home/.mozilla/firefox/x1j4g9mi.default/";
my $iwlist = "sudo /sbin/iwlist";
my $ifconfig = "sudo /sbin/ifconfig";
my $iwconfig = "sudo /sbin/iwconfig";
my $dhclient = "sudo dhclient";
my $btreceive = "$xterm -e 'echo \"Waiting for obex bluetooth...\" && sobexsrv -Id'";
my $wiface = "eth1";
my $remind  = "$xterm -e 'remind |less'";
my $edit ="$xterm -e 'vim ~/.reminders'";
my $scheduler = "$xterm -e 'EDITOR=vim wyrd'";

my @commands = (
	"mail",
	"compose",
	"dhclient",
	"agenda",
	"btreceive",
	"fetchmail",
	"screenshot",
	"browser",
	"shout",
	"notes",
	"google",
	"pkill",
	"xkill",
	"mixer",
	"music",
	"im",
	"irc",
	"irc2",
	"ssh",
	"xlock",
	"halt",
	"remind",
	"edit",
	"scheduler",
	"scratchbox",
	"wireless"
);

## Home Configuration ##

eval slurpit("$home/.dpanel.conf") || die "no conf\n";#if (-f "$home/.dpanel.conf");

## Available commands ##

my $cmd = dmenu("", @commands);

## Commands ##

if ($cmd eq "compose") {
	my $mail = resolve(dmenu("", &list));
	run(system "sylpheed --compose $mail") if ($mail);
} elsif ($cmd eq "mail") {
	system($mail);
} elsif ($cmd eq "dhclient") {
	system("xterm -bg black -fg gray -e 'system dhclient eth0'");
} elsif ($cmd eq "shout") {
	do_shout_menu();
} elsif ($cmd eq "shoutcast") {
	system("m");
} elsif ($cmd eq "fetchmail") {
	system($fetchmail);
} elsif ($cmd eq "agenda") {
	system("$xterm -fn 10x20 -e vim '$agenda'");
} elsif ($cmd eq "wireless") {
	open FD, "-|","$iwlist $wiface scan";
	while(<FD>) {
		push @aps, $1 if (/ESSID:"(.*)"/);
	}
	close FD;
	my $ap = dmenu("", @aps);
	if ($ap) {
		open FD, "-|","$iwlist $wiface scan";
		while(<FD>) {
			if (/ESSID:"(.*)"/) {
				if ($1 eq $ap) {
					while(<FD>) {
						if (/Encryption/ && /on/) {
							my $key = dmenu("wireless-key");
							system("$ifconfig $wiface up");
							system("$iwconfig $wiface essid '$ap' key '$key'");
							system("$dhclient $wiface");
							last;
						}
					}
					system("$iwconfig $wiface essid $ap");
					system("$dhclient $wiface");
					last;
				}
			}
		}
		close FD;
	}
} elsif ($cmd eq "browser") {
	open FD, "<$browser_history/history.dat" || die "no history\n";
	my @history = ();
	while(<FD>) {
		if (/http/) {
			for my $line (split(/\\/)) {
			if($line=~/http:\/\/(.*)/) {
				my $n=$1; $n=~s/\)\(.*//g; $n=~s/\).*//;
				push @history, $n;
				}
			}
		}
	}
	@history=sort @history;
	system("$browser '".dmenu("", @history)."' 2>&1 >/dev/null");
} elsif ($cmd eq "google") {
	system("$browser http://www.google.com/search?q=".dmenu()." 2>&1 >/dev/null");
} elsif ($cmd eq "pkill") {
	my $pid = dmenu("", split(/ /, `ps x | awk '{print \$5}' | sort |uniq | grep -v ^-`));
	system "pkill $pid" if ($pid);
} else {
	eval "system(\$$cmd) if (\$$cmd);";
}

## Helper Functions ##

sub dmenu {
	my $title = shift;
	my $tmp="/tmp/dpanel.$$";
	@_ = sort @_;
	open FD, "|dmenu -p $title > $tmp";
	for my $line (@_) {
		print FD "$line\n";
	}
	close FD;
	my $ret = slurpit($tmp);
	unlink($tmp);
	return $ret;
}

sub slurpit {
	my ($file) = @_;
	return undef unless (-f $file);
	open F, "<$file" || return undef;
	my $ret=""; while(<F>) { $ret.=$_; }
	close F;
	return $ret;
}

sub run {
	system $_ if (!fork());
}

sub resolve {
	my ($name) = @_;
	open FD, "<$agenda" || die "no agenda\n";
	while(<FD>) {
		chomp($_);
		my @a = split(/\t/);
		if ($a[0] eq "mail") {
			return $a[2] if ($a[1] eq $name);
		} elsif ($a[0] eq "alias") {
			if ($a[1] eq $name) {
				seek(FD, 0, 0);
				$name = $a[2];
			}
		}
	}
	close FD;
	return "";
}

sub list {
	my @names=();
	open FD, "<$agenda" || die "no agenda\n";
	while(<FD>) {
		my @a = split(/\t/);
		push @names, $a[1] if $a[0]=~/^(mail|alias)$/;
	}
	close FD;
	return @names;
}


## embed
sub do_shout_menu {

my $menu = "blues
chillout
drum and bass
jazz
techno
punk
reggae
stop";

my $ret =`echo "$menu" | dmenu`;

return if ($ret eq "");

system("pkill mplayer");
system("pkill shoutcast.pl");

return if ($ret eq "stop");

###shoutcast.pl \"$RET\" $(($RANDOM%8)) &");

do_shout($ret, 1);

#print "shuodint.\n";
}

sub do_shout {
my ($q, $o) = @_;

#//my $q=$ARGV[0]||"";
#//my $o=$ARGV[1]||"";

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
                        exit()
                if ($o ne "")
        }
        $q="";

}
