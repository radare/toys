#!/usr/bin/env perl
#
# A utility to mirror directories
# :: pancake@phreaker.net :: 20040107
# TODO : check if target file is a link
# TODO : Support for BSD libexec loaders (do automatic)

#<global>
$|=1;
my %cfg;   # HashConf
my @rms;   # Remove
my @files; # Add
my %dirs;  # MkDir
my $line=0;# LineCount
#</global>

#<main>
 if ( parseArgs() )
 {
  print "==> Mirroring using rules in '".$cfg{"file"}.
		"' to path: '".$cfg{"path"}."'.\n";
  open F,"<".$cfg{"file"} or die "Cannot open file";
  print "Creating file list... ";
  MkDir($cfg{"path"});
  while(<F>)
  {
	chomp;
	$str=$_;
	$line++;
	
	if ($str=~/\#/) { $str=~/(.*?)\#/; $str=$1; }
	chomp($str); if ($str eq "") { next; }

   	if (/^:/) { # internal option
		option($_) or die "Unknown option '$_' at line $line\n";
	} elsif (/^@/) {
		addPackage($_);
	} elsif (/^\!/) {
		Exec($_) or die "Error executing '$_' at line $line\n";
	} else {
		addFile($_);
	}
  }
  close F;
  print "OK\nCreating dependencies... ";
  foreach $f (@files)
  {
	if (! -e "$f" )
		{ die "Cannot find file: $f"; }

	if ($cfg{"libs"}==1)
	{
		if ( (-x $f) && !(-d $f))
		{
		foreach $lib (split('\n',`ldd $f 2>/dev/null`))
			{
			$lib=~/=>\s(.*)\s/; $lib=$1;
			if ( $1=~/\S/ )
				{ push (@files,$lib); }
			}
	  	}
  	}
	# Take DirNames
	$f=~/(.*)\/.*$/; $dir=$1;
	$dirs{"$dir"}=1 if ($1=~/\S/);
  }
  print "OK\nCreating paths... ";
  foreach $d (keys %dirs)
  {	MkDir($cfg{"path"}."/$d"); }

  print "OK\nCopying files... ";
  foreach $f (@files) { Copy($f); }

  print "OK\nRemoving selected files... ";
  foreach $f (@rms) { Rm($f); }
  print "OK\nDONE\n";
 }
#</main>

#<addFile>
sub addFile()
{
	($f)=@_;
	my @dest;

	if ($f=~/^\-/)
	{ $dest=\@rms;   $f=~s/.//; }
	elsif ($f=~/^\+/)
	{ $dest=\@files; $f=~s/.//; }
	else { $dest=\@files; }

	if ( -d "$f" ) {
		foreach $f (split(' ',`find $f`))
		{ push @$dest,$f; }
	} else {
	    push @$dest,$f;
	}
}
#</addFile>

#<addPackage>
sub addPackage()
{
	($pkg)=@_;
	my @dest;

	$pkg=~s/.//;

	$dest=\@files;
	if ($pkg=~/^-/)
	{ $dest=\@rms; $pkg=~s/.//; }

	$pkgfiles="";
	if ($cfg{"pkg"}eq"pkgsrc")
	{	$pkgfiles=`pkg_info -L $pkg`;
	} elsif ($cfg{"pkg"}eq"debian") {
		$pkgfiles=`dpkg -L $pkg`;
	} elsif ($cfg{"pkg"}eq"gentoo") {
		$pkgfiles=`qpkg -l -nc $pkg`;
	} else {
		die "Package system not defined";
	}
	if (! ("$!" eq ""))
	  { die "\nCommand not found to manage '".$cfg{"pkg"}."'"; }

	# ADD FILES
	foreach $f (split('\n',$pkgfiles))
	{
		chomp($f);
		if ($f=~/^\//)
		{ push(@$dest,$f); }
	}
}
#</addPackage>

#<MkDir>
sub MkDir()
{
  ($dir)=@_;
  if ($cfg{"verb"}==1)
	{ print "MKDIR $dir\n"; }
  if (!(-e $dir))
    { system("mkdir -p $dir") == 0 or die "Cannot create dir: $dir"; }
  if (! ( -d $dir ))
    { die "$dir isn't a directory\n"; }
}
#</MkDir>

#<Rm>
sub Rm()
{
  ($f)=@_;
  if ($cfg{"verb"}==1)
  	{ print "RM $f\n"; }
  `rm -rf $cfg{"path"}/$f`;
  # TODO Check if exists? # enable strict
}
#</Rm>

#<Exec>
sub Exec()
{
   ($cmd)=@_;
   $cmd=~s/.//;
   system("cd ".$cfg{"path"}." && $cmd && cd -") == 0
   	or return 0;
   return 1;
}
#</Exec>

#<option>
sub option()
{
	($opt)=@_;
	my $val=1;  $val=0 if ($opt=~/\!/);
	if    ($opt=~/libs/)   { $cfg{"libs"}=$val;    } # directives
	elsif ($opt=~/verb/)   { $cfg{"verb"}=$val;    }
	elsif ($opt=~/into/)   { $cfg{"into"}=$val;    }
	elsif ($opt=~/pkgsrc/) { $cfg{"pkg"}="pkgsrc"; } # pkg systems
	elsif ($opt=~/debian/) { $cfg{"pkg"}="debian"; }
	elsif ($opt=~/gentoo/) { $cfg{"pkg"}="gentoo"; }
	else { return 0; }
    return 1; # ok
}
#</option>

#<Copy>
sub Copy()
{
  ($f)=@_;
  if ( -d $f ) { return; } # Skip
  if ( -e $cfg{"path"}."/$f" )
  {
    return;
  }
  #HardLink doesn't works on chroots ://
  system("cp $f ".$cfg{"path"}."/$f") == 0
;#		or die "Cannot hardlink file: $f\n";
}
#</Copy>

#<parseArgs>
sub parseArgs()
{	if ($#ARGV<1)
	{	print "use ./me [rulesfile] [rootpath]\n";
		return 0; }
	if ($ARGV[0]eq"-")
	  { $cfg{"file"}="/dev/stdin"; } else
	  { $cfg{"file"}=$ARGV[0]; }
	$cfg{"path"}=$ARGV[1];
	$cfg{"meth"}="ln -d";  # Use hard links by default XXX
	return 1;
}
#</parseArgs>
