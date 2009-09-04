#!/usr/bin/env perl
#  _____ ____ ___
# |_   _'  - `  _| Jabber *
#  _| | |  .-| |_  Perl   * pancake@phreaker.net
# |___| |__| |___| Client * updated (2004-06-20)
# 

# TODO handle /${alias} or /${jid} as /q ${alias|jid}
# TODO handle /Q as /q

$version="0.7";
binmode STDOUT, ':iso8859';

#use threads;
#use threads::shared;
use Encode; # TODO (autodetect)

sub doError
{
	($type)=@_;
	if ($type eq "config") {
		print <<_EOF_;
# Please edit your ~/.jpc.conf file with:
 \$username = "your_username";
 \$password = "your_password";
 \$server   = "your_server.org";
# Other options.. \$resource, \$register=1, \%alias, \$resource, \$ansi=1, \$autoaway=60
#   \$ghost=0, \$navigator="links -g", \$away="default away msg", \$port, \$prompt
#   \$sufix="jabber.org" \$usereadline=0
_EOF_
	} elsif ($type eq "jabber_module") {
		print "Please install Net::Jabber CPAN module.\n";
	}
	exit 1;
}

$usereadline=0;
$autoaway=0;
$register=0;
$away="away";
if (!$navigator){$navigator="links"; }
$ghost=0;
$port=5222;
if (!$resource) { $resource="jpc (pancake client)"; }
$prompt="jpc";
$prefix="/";
$ansi=1;
if (!$sufix) { $sufix="nopcode.org"; }
%alias;


sub CompleteJid
{
	($str)=@_;
	if (! ($str=~/\@/) )
		{
		$str.="\@".$sufix;
		}
	return $str;
}

sub color
{
	($type)=@_;
	if ($ansi==0) { return; }
	if ($type eq "alert") {
		print "\e[31m";
	} elsif ($type eq "info") {
		print "\e[32m";
	} elsif ($type eq "prompt") {
		print "\e[32m";
	} elsif ($type eq "target") {
 		print "\e[33m";
	} elsif ($type eq "status") {
		print "\e[37m";
	} elsif ($type eq "other") {
		print "\e[35m";
	} else {
		print "\e[0m"; }
}

if (! -e "$ENV{HOME}/\.jpc\.conf" )
	{ doError("config"); }
require "$ENV{HOME}/\.jpc\.conf";
if ( $username eq "" || $server eq "" || $password eq "" )
	{ doError("config"); }
color("info");
print "Loading Jabber Perl Client... v$version\n";
color("");
eval "use Net::Jabber qw(Client);";
doError("jabber_module") if $@;
if ($usereadline==1) {
	use Term::ReadLine;
}

my $con:shared;      # Connection object
my $query:shared=""; # Default nick to chat
my %roster:shared;
my $th:shared;

my $url="";
sub LoadURL
{
	my $u=$url;
	$u=~s/&/\\&/g;
	if ($navigator eq "") {
		print "[E] Navigator disabled.\n";
	} else {
		system("$navigator $u");
	}
}

$controlc=0;
sub ControlC
{
	$controlc++;
	if ($controlc==3) {
		InQuit();
		exit();
	} else {
		print "\n";
	}
}
sub PrintPrompt
{
	color("prompt"); # Reset color 
	print "$prompt";
	alarm($autoaway);
	if (! ($query eq "")) { 
		color("target");
		print "\:$query"; 
		color("prompt");
	} 
	print "> ";
	color("");
}

sub Reload
{
	printf("=>reload\n");
	require "$ENV{HOME}/\.jpc\.conf";
}

sub ListUsers
{
	print "\n";
	color("info");
	print "List of users:\n";
	foreach $key (keys %roster)
	{
	$jid=$key;$jid=~/\/([^\n]*)/;
	$res=$1;$jid=~s/\/.*//;
	foreach $ali (keys %alias)
	{
		if ( $alias{$ali} eq $jid)
		{
		$jid=$ali;
		last;
		}
	}
	$pos=20-length($jid); if ($pos<0){$pos=0;}
	$pos2=10-length($res); if ($pos2<0){$pos2=0;}
	print " @ $jid"." "x$pos." (".$res.") "." "x$pos2."".$roster{$key}."\n";
	#printf(" @ %030s - %s\n",$jid,$roster{$key});
	#print " @ ".$jid." \t - ".
	#	$roster{$key}."\n";
	}
	color("");
	print "\e[0m";
}

sub ReadText
{
	my $msg="";

	print "Type your message, ending with \".\" \n";

	while(1) # Read Message
	{
		$line=<STDIN>;
		if ($line eq "") { 
			select(undef, undef, undef, 0.1); # it means a FreeBSD bug?
			next; 
		}
		$msg.=$line;
		if ($msg=~/\n.\n$/) {
			$msg=~s/\n.\n$//;
			last;
		} 
	}

	return $msg;
}

sub SendStatus
{
	($show,$status)=@_;
	if ($status eq "<") {
		$status=ReadText();
	}
	$pres=new Net::Jabber::Presence();
	$pres->SetPresence(status=>"$status",show=>"$show");
	$con->Send($pres);
	print "[S] You are '$show' ($status).\n";
}

sub AutoAway
{
	SendStatus("away",$away);
}

sub jabber_loop {
	print "JabberLoop()\n";
	$SIG{ILL}=\&ListUsers;
	$SIG{BUS}=\&LoadURL;
	$SIG{SYS}=\&Reload;
	$SIG{INT}=0;
	while($con->Process()){ print "Processed"; }
	print "\n\nConnection closed.\n";
	kill ( SIGINT, getppid() );
	exit;
}

## Main ##
{
	$con = Net::Jabber::Client->new();
	$con->SetCallBacks(
		"message"  => \&InMessage,
		"presence" => \&InPresence,
		"iq"       => \&InIQ );
	
	print "Connecting to $server...";
	$con->Connect("hostname"=>"$server","port"=>$port);
	
	if ($con->Connected())
	{	print "OK\n";
	} else {
		print ("ERR\n");
		exit 1;
	}
	# Safe exit :)
	$SIG{HUP}=\&InQuit;
	$SIG{KILL}=\&InQuit;
	$SIG{TERM}=\&InQuit;
	$SIG{ALRM}=\&AutoAway;
	if ($register == 1)
	{
		print "Registering... ";
		$con->RegisterSend(
			username=>"$username",
			resource=>"$resource",
			password=>"$password");
		print "SENT\n";
	}

	print "Authenticating... ";
	my @msg=$con->AuthSend(
		"username" => "$username",
		"password" => "$password",
		"resource" => "$resource");
	
	if ($msg[0] ne "ok") {
		print "Error $msg[0]::$msg[1]\n";
		exit;
	} else {
		print "OK\n";
	}

	print "Fetching Roster...";
	$con->RosterGet();
	print "OK\n";

	if ($ghost==1) {
		color("info");	
		print "Ghost mode ON...roster will not be received.\n";
		color("");
	} else {
		$con->PresenceSend();
		# TODO get all roster
		#       os.println("<iq type='get' id='caca'>"+
      		#       "<query xmlns='jabber:iq:roster'/></iq>");
	}

	$th=fork();
	#$th = threads->new(\&jabber_loop); #"jabber_loop","");
	if(!$th)
	{       # Main Loop
		$SIG{ILL}=\&ListUsers;
		$SIG{BUS}=\&LoadURL;
		$SIG{SYS}=\&Reload;
		$SIG{INT}=0;
		while($con->Process()){}
		print "\n\nConnection closed.\n";
		kill ( SIGINT, getppid() );
		exit;
	} else { # CMDLINE
		$SIG{INT}=\&ControlC;
		$controlc=0;
		print "cumming\n";
		if ($usereadline) {
			$term=new Term::ReadLine 'xxx';
		}

		while(1) {
		$kc;
		ONLOOP:
		PrintPrompt();

		# Read CmdLine
		$k_old=$k;
		do {
			if ($usereadline){
				$k=$term->readline();
				$term->addhistory($k);
			} else {
				$k=<STDIN>;
			}
			if ($k eq "")
			 { 
			  if ($kc==0 && $controlc==1) 
			  { 
				$kc=1; 
				goto ONLOOP; 
			  }
			 select(undef, undef, undef, 0.1); 
			}# it means a FreeBSD bug?
		} while($k eq "");
		$k=~s/\n$//;
		$kc=0;
		
		if ($k eq "")
			{ next; # DO nothing
			}
		elsif ($k=~/^!$/) # repeat last command
			{
			$k=$k_old;
			}
		$controlc=0;

		if ($k=~/^\/help/ || $k=~/^help/)
			{
			print "[?] Commands Help:\n";
			print "  Messages: /msg  /mail /query /list /global\n";
			print "  Client:   /quit /clear /reload /autoaway\n";
			print "  Roster:   /list /subscribe /accept /drop /alias /noadmit /readmit\n";
			print "  Presence: /away /online /ghost /status /presence [-]jid\n";
			print "  Actions:  /link \n";
			}
		elsif ($k=~/^\/autoaway (.*)/)
			{
			# TODO check if it's a number
			print "[%] Autoaway set to $1 seconds.\n";
			$autoaway=$1;
			}
		elsif ($k=~/^\/presence (.*)/)
			{
			$target=$1;
			# Other types:
			#  available/unavailable/subscribe/probe...
			if ($target=~/^-/) {
				$target=~s/-//;
				print "Unpresencing $target\n";
				$type="visible";
			}else {
				print "Presencing to $target\n";
				$type="invisible";
			}
			my $presence = new Net::Jabber::Presence(); #To=>$target);
			$presence->SetTo($target);
			$presence->SetType($type);
			$con->Send($presence);
			}
		elsif ($k=~/^\/accept (.*)/)
			{
			print "Accepting suscribe of '".$1."'\n";
			#OutMessage($1,"accepted","subscribed");
			$con->Subscription(type=>"subscribe",to=>"$1");
			$con->Subscription(type=>"subscribed",to=>"$1");
			#$con->Subscription(type=>"subscribe",to=>"$1");
			}
		elsif (($k=~/^\/subscribe (.*)/) ||
			($k=~/^\/suscribe (.*)/) )
			{
			print "Asking for suscription to: $1.\n";
		    	$con->Subscription(type=>"subscribe",to=>"$1");
			#OutMessage($1,"suscribe reason :)","subscribe");
			}
		elsif ($k=~/^\/drop (.*)/)
			{
			print "User $1 dropped from both rosters\n";
			$con->Subscription(type=>"unsubscribe",to=>"$1");
			$con->Subscription(type=>"unsubscribed",to=>"$1");
			}
		elsif ($k=~/^\/noadmit (.*)/)
			{
			print "You was droped from the $1 roster.\n";
			$con->Subscription(type=>"unsubscribed",to=>"$1");
			}
		elsif ($k=~/^\/readmit (.*)/)
			{
			print "User $1 is readmitted.\n";
			$con->Subscription(type=>"subscribed",to=>"$1");
			}
		elsif ($k=~/^\/clear/)
			{
			print "\e[2J";
			}
		elsif ($k=~/^\/quit/)
			{
			InQuit();
			}
		elsif ($k=~/^\/reload/)
			{
			if ( -e "$ENV{HOME}/\.jpc\.conf" )
				{
				color("info");
				Reload();
				kill SYS,$th;
				require "$ENV{HOME}/\.jpc\.conf";
				print "==> Reload OK.\n";
				color("");
				}
			}
		elsif ($k=~/^\/msg/)
			{
			if ($query eq "")
				{
				print "You must query somebody.\n";
				} else {
				$msg=ReadText();
				OutMessage($query,$msg,"chat");
				}
			}
		elsif ($k=~/^\/msg (.*)\s([^\n]*)$/)
			{
			$to=CompleteJid($1);
			if ($alias{$1}) { $to=$alias{$1}; }
			print "=> $to: $2\n";
			OutMessage($1,$2,"chat");
			}
		elsif ($k=~/^\/global ([^\n]*)$/)
			{
			$msg=$1;
			if ($msg eq "<")
				{
				$msg=ReadText();
				}
			OutMessage("$server/announce/online",$msg,"chat");
			}
		elsif ($k=~/^\/mail (.*)/ || $k=~/^\/m (.*)/ )
			{
			$to=$1;
			$msg="";
			print "Type your message, ending with \".\" \n";
			while(1) # Read Message
			{ $msg.=<STDIN>; if ($msg=~/\n.\n$/) { last; } }
			print "Mail sent.\n";
			OutMessage($to,$msg,"normal");
			}
		elsif ($k=~/^\/query (.*)/ || $k=~/^\/q (.*)/)
			{
			$query=CompleteJid($1);
			if ($alias{$1}) { $query=$alias{$1}; }
			print "Query to $query\n";
			}
		elsif ($k=~/^\/query/)
			{
			print "Query undefined\n";
			$query="";
			}
		# ALIAS #
		elsif ($k=~/^\/alias (.*) (.*)$/)
			{
			print "[=] Alias $1 assigned to $2\n";
			$alias{$1}=$2;
			}
		elsif ($k=~/^\/alias (.*)$/)
			{
			print "[=] Alias $1 removed from list\n";
			delete $alias{$1};
			}
		elsif ($k=~/^\/away ([^\n]*)/)
			{
			SendStatus("away",$1);
			}
		elsif ($k=~/^\/away$/)
			{
			SendStatus("away",$away);
			}
		elsif ($k=~/^\/online/)
			{
			SendStatus("available","");
			}
		elsif ($k=~/^\/ghost/)
			{
			print "[S] You are a fucking ghost\n";
			$pres=new Net::Jabber::Presence();
			$pres->SetPresence(type=>"invisible"); 
			$con->Send($pres);
			}
		elsif ($k=~/^\/status/)
			{
			# TODO
			print "Connection: ".$con->Connected()."\n";
			print "Status: ".$away." <-- TODO\n";
			}
		elsif ($k=~/^\/link/)
			{
			kill BUS,$th;
			}
		elsif ($k=~/^\/alias/)
			{
			print "[=] Alias list\n";
			foreach $key (keys %alias)
				{
				print " * $key => $alias{$key}\n";
				}
			}
		elsif ($k=~/^\/list/)
			{
			#ListUsers();
			kill ILL,$th;
			}
		else    {
				if (!$query)
				{
					print "Invalid command '$k' ... Try using /help\n";
				} else {
					OutMessage($query,$k,"chat");
				}
			}
		$old_k=$k;
		}
	}

	exit;
}

sub OutMessage
{
	my ($who,$msg,$type)=@_;
	$who=CompleteJid($who);
	$msg=Encode::encode("utf8",$msg);
	if ($alias{$who}) { $who=$alias{$who}; }
	$msg=~s/\n$//g;
	$m=new Net::Jabber::Message();
	$m->SetTo($who); $m->SetType($type);
	$m->SetBody($msg);
	$con->Send($m);
}

# Message
sub InMessage
{
	($sid,$msg)=@_;
	$body=$msg->GetBody();
	$body=Encode::decode("utf8", $body);
	if ($msg->GetType() eq "chat")
	{
		if ($msg->GetFrom() eq $query)
		{ color("target"); } else { color("other"); }
		print "\n<",$msg->GetFrom(),"> ";
		color("");
		print "$body\n";
		if ($body=~/http:\/\/(.*)/)
		{
			$url="http://$1";
			color("info");
			print "[U] Type '/link' to load '$url'.\n";
			color("");
		}
	}
	elsif ($msg->GetType() eq "normal" ||
		$msg->GetType() eq "" )
	{
		if ( length($body) > 0 ) {
		print "\n[ MAILFRM: ".$msg->GetFrom()." ]";
		print "\n[ SUBJECT: ".$msg->GetSubject()." ]"
			 if ($msg->GetSubject());
		print "\n=======================================\n";
		print $body;
		print "\n=======================================\n";
		}
	} elsif ($msg->GetType() eq "error") {
		color("alert");
		print "\n[ERROR] <".$msg->GetFrom()."> ".$body."\n";
		color("");
	} else {
		print "Message type: '".$msg->GetType().
		"' not yet supported. Recived from ".$msg->GetFrom()."\n";
	}
}

# Enter/Exits
sub InPresence
{
	($sid,$prs)=@_;
	color("status");
	if ($prs->GetType() eq "unavailable")
	{
		print "\r[<] ".$prs->GetFrom()." exits.\n";
		delete $roster{$prs->GetFrom()};
	}
	elsif ($prs->GetType() eq "subscribe")
	{
		print "\n[SUSCRIBE] ".$prs->GetFrom()." wants to suscribe you.";
		print "\n[SUSCRIBE] Type '/accept ".$prs->GetFrom()."' to accept.\n";
	}
	elsif ($prs->GetType() eq "unsubscribe")
	{
		print "\n[UNSUSCRIBE PETITION RECIVED] ".$prs->GetFrom();
		print "\n[UNSUSCRIBE] Type '/unsuscribed ".$prs->GetFrom()."'\n";
	} else {
		if ($prs->GetFrom()=~/\//)
		{
		$status=$prs->GetStatus();

		$status=~s/^\n*//;
		$status=~s/\n*$//;
		foreach $key (keys %roster)
		{
		if ( "$key" eq $prs->GetFrom() )
			{
			$oldstatus=$roster{$key};
			if (! ("$oldstatus" eq "$status") )
				{
				print "[S] $key changes status to '".$status."'.\n";
				$roster{$key} = $status;
				}
			goto MsgInEnd;
			}
		}
		print "\r[>] Presence of ".$prs->GetFrom()." (". $status
			.") - ".$prs->GetType()."\n";
		MsgInEnd:
		$roster{$prs->GetFrom()}=$status;
		}
	}
	color("");
}


# Info/Query
sub InIQ
{
	($sid,$iq)=@_;
	#print "\n[iQ] From: ",$iq->GetFrom()," xmlns: ",
	#	($iq->GetQuery())->GetXMLNS(),"\n";
}

sub InQuit
{
   print "Disconnecting...\n";
   $con->Disconnect();
   $th->join();
   exit;
}
