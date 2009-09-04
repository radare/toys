#!/usr/bin/env perl -w
#
# author:  pancake <pancake@youterm.com>
# version: 0.3
#
# Converts an XML registry file into a .reg one and viceversa
#
#   Greetz to pof && 3des
#
# Usage:
#  $ g-cpan XML::Registry
#  $ emerge XML-Registry
#  $ cat my-reg.xml | perl xml2reg.pl > my-reg.reg

use XML::Parser;
use XML::Registry;

my $dump   = new XML::Registry;
my $parser = new XML::Parser(Style => 'Tree');

sub show_help_message {
	print "Usage:\n";
	print " xml to reg: \$ cat my-reg.xml | perl xml2reg.pl > my-reg.reg\n";
	print " reg to xml: \$ cat my-reg.reg | perl xml2reg.pl -i > my-reg.xml\n";
}

if ( defined($ARGV[0]) && $ARGV[0] eq "-i" ) {
	my $level = 0;
	while(<STDIN>) {
		my $str=$_;
		if ($str=~/^\"/) {
			if ($str=~/"=dword:/) {
				$str=~/"(.*)"=dword:(.*)/;
				print "\t\t\t<parm name=\"$1\" datatype=\"integer\" value=\"".eval("0x$2")."\" />\n";
			} else {
				$str=~/"(.*)"="(.*)"/;
				next unless defined $1;
				my $value = defined($2)?$2:"";
				my $key = $1;
				$key="Default" if ($key eq "@");
				$value=~s/\\\\/\\/g;
				print "\t\t\t<parm name=\"$key\" datatype=\"string\" value=\"$value\" translation=\"filesystem\"  />\n"; }
		} elsif($str=~/REGEDIT4/) {
			print "<wap-provisioningdoc>\n";
			print "\t<characteristic type=\"Registry\">\n";
		} elsif($str=~/^\[/) {
			$str=~/\[(.*)\]/;
			print "\t\t</characteristic>\n" if ($level++);
			$domain=$1;
			$domain=~s/HKEY_LOCAL_MACHINE/HKLM/;
			$domain=~s/HKEY_CURRENT_USER/HKCU/;
			$domain=~s/HKEY_CLASSES_ROOT/HKCR/;
			print "\t\t<characteristic type=\"$domain\"  translation=\"filesystem\" >\n";
		}
	}
	print "\t\t</characteristic>\n" if ($level++);
	print "\t</characteristic>\n";
	print "</wap-provisioningdoc>";
} elsif (defined($ARGV[0]) && $ARGV[0] eq "-h" ) {
	&show_help_message;
} else {
	my $mytree = $parser->parse(join("",<STDIN>));
	print "REGEDIT4\n";
	&recursetree($mytree->[0], $mytree->[1]);
	print "\n";

	sub recursetree {
		local ($el, $tree) = @_;

		for (my $i=0; $i < scalar(@$tree); $i++) {
			if (ref($tree->[$i]) eq 'ARRAY') {
				&recursetree($tree->[$i-1], $tree->[$i]);
			} elsif (ref($tree->[$i]) eq 'HASH') {
				my $att = $tree->[$i];
				if ($el eq "characteristic") {
					foreach my $attrib (keys(%$att)) {
						if ($attrib eq "type") {
							my $domain = $att->{$attrib};
							last if ($domain=~/Registry/);
							$domain=~s/HKLM/HKEY_LOCAL_MACHINE/;
							$domain=~s/HKCU/HKEY_CURRENT_USER/;
							$domain=~s/HKCR/HKEY_CLASSES_ROOT/;
							print "\n[$domain]\n";
							last
						}
					}
				} elsif ($el eq "parm") {
					my $key;
					my $value;
					my $type="dword";
					foreach my $attrib (keys(%$att)) {
						if ($attrib eq "name") {
							$key=$att->{$attrib};
						}elsif ($attrib eq "value") {
							$value=$att->{$attrib};
						}elsif ($attrib eq "datatype") {
							$type = $att->{$attrib};
						}
					}
					$key=~s/Default/@/;
					$value=~s/\\/\\\\/g;
					if ($type eq "string") {
						print "\"$key\"=\"$value\"\n";
					} else {
						printf "\"$key\"=dword:%x\n", $value;
					}
				}
			}
		}
	}
}
