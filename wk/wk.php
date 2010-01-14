<?
$WKDB="/home/x90/wikidb";
$PASS="ass";
$TITLE="Test wiki";
$BIN="http://www.nopcode.org/wk.php";
$PATH_INFO=pathinfo($_SERVER["REQUEST_URI"]);
#$PATH_INFO=(pathinfo($_SERVER["REQUEST_URI"]));
$PATH_INFO=preg_replace("/\?.*$/","", $PATH_INFO["filename"]);

if (is_dir($WKDB."/".$PATH_INFO)) {
	$PATH_INFO=$PATH_INFO."/Main";
}

function wikilinks($f) {
	$str = file_get_contents($f);
	$str = @preg_replace("/</","&lt;", $str);
	$str = @preg_replace("/>/","&lt;", $str);
	$str = @preg_replace("/---/","<hr size=1 />", $str);
	$str = @preg_replace("/\n/","<br />", $str);
	$str = @preg_replace("/\[\+\+\+/","<h3>", $str);
	$str = @preg_replace("/\+\+\+\]/","</h3>", $str);
	$str = @preg_replace("/\[\+\+/","<h2>", $str);
	$str = @preg_replace("/\+\+\]/","</h2>", $str);
	$str = @preg_replace("/\[\+/","<h1>", $str);
	$str = @preg_replace("/\+\]/","</h1>", $str);
	$str = @preg_replace("/\[console\]/", '<div class="console">', $str);
	$str = @preg_replace("/\[\/console\]/","</div>", $str);
	$str = @preg_replace("/\[_/","<u>", $str);
	$str = @preg_replace("/_\]/","</u>", $str);
	$str = @preg_replace("/\[img=([^\]]*)\]/","<img src='$1' \/>", $str);
	$str = @preg_replace("/\[\[([^\]]*)\]\[([^\]]*)\]\]/",'<a href="$1">$2</a>', $str);
	$str = @preg_replace("/\[\[http:\/\/([^\]]*)\]\[([^\]]*)\]\]/e",'<a href=http://$1>$2</a>',$str);
	$str = @preg_replace("/h(\d)>(.)<br \/>/", 'h$1>$2', $str);
	print $str;
}

//function urldecode() {
	// TODO : reimplement?
//}

function show_css() {
?>
<html>
<title><? echo $TITLE; ?> / wk</title>
<style>
.console {
	background-color:#303030;
	color:#f0f0f0;
	font-size:12px;
	font-family:monospace;
	padding:5px;
}
body {
	font-family:Sans-Serif,Verdana;
	color:#e0e0e0;
	background-color:#202020;
	background-color:#000000;
}
input, textarea {
	background-color:#202020;
	font-family:Sans-Serif,Verdana;
	font-size:14px;
	border:0px;
	color:#606060;
	font-family:monospace;
}
hr {
	background-color:gray;
	border:01px;
	width:75%;
}
input:focus, textarea:focus {
  color:#a0a0a0;
  background-color: #303030; 
}
.menubar {
	width:150px;
	background-color:#000000;
}
div{
	background-color:#303030;
	color:#c0c0c0;
}
a {
	color:#7080c0;
	text-decoration:none;
}
a:hover {
	color:#a0b0f0;
	text-decoration:underline;
}
</style>
<body>
<?
}

function show_header()
{
	global $PATH_INFO;
?>
<img src=http://www.nopcode.org/nopcode2.png>
<div style="width:100%">
<table width=100%>
<tr><td><a href=Main>wk</a> <? echo $PATH_INFO; ?></td>
<td align=right>
 <a href="?list">list</a>
 <a href="?search">search</a>
 <a href="?blog">blog</a>
 <a href="?">view</a>
 <a href="?edit">edit</a>
</td></tr></table>
</div>
<br />
<?
}

function do_edit() {
global $WKDB;
global $PATH_INFO;
$PAGE=@file_get_contents($WKDB."/".$PATH_INFO);
if ($PAGE=="") {
	?> <h2>New page: <? echo $PATH_INFO."</h2>";
} else {
	?> <h2>Edit page: <? echo $PATH_INFO."</h2>";
}
?>
<center>
<form action="?save" method="post">
<textarea name=text style='width:90%' rows=24><? echo $PAGE; ?></textarea>
<br />
<table width=90%>
<tr>
 <td align=left>Password:
  <input name=pass style='width:100px' type=password>
</td><td align=right>
  <input name=remove type=checkbox> Remove
  <input type=submit value=Submit>
</td></tr>
</table>
</form>
</center>
<?
}

function do_save() {
	global $WKDB;
	global $PATH_INFO;
	if (isset($_POST["remove"])) {
		if (file_exists($WKDB."/".$PATH_INFO)) {
			echo "<a href=Main>Removed</a>";
			unlink($WKDB."/".$PATH_INFO);
		} else {
			echo "Page does not exist";
		}
	} else {
		echo "<a href=$PATH_INFO>( $PATH_INFO Saved )</a>";
		file_put_contents($WKDB."/".$PATH_INFO, $_POST["text"]); //urldecode($_POST["text"]));
		//echo $1 | cut -d '&' -f 1 | cut -d '=' -f 2 | urldecode > ${WKDB}/${PATH_INFO}
	}
}


function byebye() {
	echo "</body></html>";
	exit( 0);
}

/* printage */
show_css();
show_header();

echo "<table width=100%><tr><td class=menubar valign=top>";
if (file_exists($WKDB."/MenuBar")) {
	wikilinks($WKDB."/MenuBar");
} else {
	echo "<a href=MenuBar?edit>edit MenuBar</a>";
}
echo '</td><td valign="top">';

switch($_SERVER["QUERY_STRING"]) {
case "list":
	echo "<h2>Entries</h2>";
	$dh = opendir($WKDB);
	// TODO: sort
	while($file=readdir($dh)) {
		if ($file[0]!=".")
		echo "<a href=$file>$file</a><br />";
	}
	closedir($dh);
	break;
case "search":
	echo "<form action=?search method=post>" ;
  	echo "Search: <input name=keyword style='width:200px'>";
  	echo "<input type=submit value=Submit>";
	echo "</form>";
	if ( $_SERVER["REQUEST_METHOD"] == "POST" ) {
		#KEYWORD=`cat - | cut -d = -f 2`
		echo "<table width=60%>";
		// TODO: sort
		$KEYWORD=$_POST["keyword"];
		$total=0;
		if (strlen($KEYWORD)>3) {
		$dh = opendir($WKDB);
		while(($file=readdir($dh))) {
			if ($file[0]!=".") {
				$str = file_get_contents($WKDB."/".$file);
				//$n = strstr($str, $KEYWORD);
				$coins=array();
				$n = @preg_match_all("/$KEYWORD/e", $str, $coins);
				if ($n>0) {
					echo "<tr><td><a href=$file>$file</a></td><td>$n hits...</td></tr>";
					// TODO show context
					$total+=$n;
				}
			}
		}
		closedir($dh);
		}
		echo "</table>";
		if ($total==0) echo "<h3>No results</h3>"; else echo "<h3>$total hits</h3>";
	}
	break;
case "blog":
	echo "<h2>Blog (TODO)</h2>";
	/*
	FILES=`cd db && ls -t Blog.* 2>/dev/null`
	for a in $FILES; do
		echo "<br/><br /><a href=$a>$a</a><br />";
		#perl -e "\$a=\"${WKDB}/$a\";" -e 'local($sec,$min,$hr,$day,$mon,$yr,$wday,@dntcare) = localtime((stat("$a"))[9]); print ($yr+1900); print "-$mon-$day $hr:$min:$sec<hr />";'
		wikilinks ("${WKDB}/$a");
		echo "<br /><br />";
	}
	*/
	break;
case "save":
	if ( $_SERVER["REQUEST_METHOD"] == "POST" ) {
		$TEXT=$_POST["text"];
		if ( $PASS == "" ) {
			do_save("");
		} else {
			if ( $_POST["pass"] == $PASS ) {
				do_save($TEXT);
			} else {
				echo "Invalid password";
			}
		}
	} else {
		echo ("Oops");
		show_vars();
	}
	byebye();
	break;
case "edit":
	do_edit();
	break;
default:
	if (file_exists($WKDB."/".$PATH_INFO)) {
		wikilinks($WKDB."/".$PATH_INFO);
	} else {
		do_edit();
	}
	break;
}

echo "</td></tr></table>";
byebye();

?>
<!--
#!/bin/sh

WKDB="db"         # Directory to place data
PASS="food"       # Edit password
TITLE="Test wiki" # Title of the wiki
BIN=`basename $0` # wk - hardcode if not necessary

echo "Content-type: text/html"
echo

if [ -z "`echo ${REQUEST_URI} | grep ${BIN}/`" ]; then
	echo "<script>window.location=\"${BIN}/\";</script>"
	exit 0
fi

if [ -d "${WKDB}/${PATH_INFO}" ]; then
	PATH_INFO="${PATH_INFO}/Main"
fi
PATH_INFO=`echo $PATH_INFO| sed -e 's,[^a-zA-Z0-9\.],,g'`
#PATH_INFO=`echo $PATH_INFO| sed -e 's,/,,g' -e 's,|,,g' -e 's,\`,,g' -e 's,$,,g'` 

wikilinks() {
PRG='
s/</&lt;/g;
s/>/&gt;/g;
s/\[\+\+/<h2>/g;
s/\+\+\]/<\/h2>/g;
s/\[\+/<h1>/g;
s/\+\]/<\/h1>/g;
s/\[console\]/<div style="background-color:black;font-size:10px;font-family:monospace;padding:5px">/g;
s/\[\/console\]/<\/div>/g;
s/\[_/<u>/g;
s/_\]/<\/u>/g;
s/\[i\]/<i>/g;
s/\[\/i\]/<\/i>/g;
s/\[right\]/<p align=right>/g;
s/\[\/right\]/<\/p>/g;
s/\[img=(.*)\]/<img src=$1 \/>/g;
s/\[\[http:\/\/(.*)\]\[(.*)\]\]/<a href=http:\/\/$1>$2<\/a>/g;
s/\[\[\^(.*)\]\[(.*)\]\]/<font color=$1>$2<\/a>/g;
s/\[\[(.*)\]\[(.*)\]\]/<a href="$1">$2<\/a>/g;
print "$_<br />";
'
cat $1 | perl -ne "${PRG}"
}

urldecode() {
awk '
BEGIN {
	hextab ["0"] = 0; hextab ["8"] = 8;
	hextab ["1"] = 1; hextab ["9"] = 9;
	hextab ["2"] = 2; hextab ["A"] = hextab ["a"] = 10
	hextab ["3"] = 3; hextab ["B"] = hextab ["b"] = 11;
	hextab ["4"] = 4; hextab ["C"] = hextab ["c"] = 12;
	hextab ["5"] = 5; hextab ["D"] = hextab ["d"] = 13;
	hextab ["6"] = 6; hextab ["E"] = hextab ["e"] = 14;
	hextab ["7"] = 7; hextab ["F"] = hextab ["f"] = 15;
} {
	decoded = ""
	i   = 1
	len = length ($0)
	while ( i <= len ) {
		c = substr ($0, i, 1)
		if ( c == "%" ) {
			if ( i+2 <= len ) {
				c1 = substr ($0, i+1, 1)
				c2 = substr ($0, i+2, 1)
				if ( hextab [c1] == "" || hextab [c2] == "" ) {
					print "WARNING: invalid hex encoding: %" c1 c2 | "cat >&2"
				} else {
					code = 0 + hextab [c1] * 16 + hextab [c2] + 0
					c = sprintf ("%c", code)
					i = i + 2
				}
			} else {
				print "WARNING: invalid % encoding: " substr ($0, i, len - i)
			}
		} else if ( c == "+" ) {
			c = " "
		}
		decoded = decoded c
		++i
	}
	print decoded
}'
}

cat << _css_
<html>
<title>${TITLE} / wk</title>
<style>
body {
	font-family:Verdana;
	color:#e0e0e0;
	background-color:#202020;
}
input, textarea {
	background-color:#909090;
	font-family:Verdana;
	font-size:14px;
	border:0px;
	color:#101010;
	font-family:monospace;
}
input:focus, textarea:focus {
  color:black;
  background-color: #c0c0c0; 
}
.menubar {
	background-color:#202020;
}
div{
	background-color:#303030;
	color:#c0c0c0;
}
a {
	color:#7080c0;
	text-decoration:none;
}
a:hover {
	color:#a0b0f0;
	text-decoration:underline;
}
</style>
<body>
_css_


show_vars() {
	echo "<pre>"
	env
	echo "</pre>"
}

#PAGE=`show_vars`

do_edit() {
PAGE=`cat "${WKDB}/${PATH_INFO}" 2>/dev/null`
cat << _edit_
<center>
<form action="?save" method="post">
<textarea name=text style='width:90%' rows=24>${PAGE}</textarea>
<br />
<table width=90%>
<tr>
 <td align=left>Password:
  <input name=pass style='width:100px' type=password>
</td><td align=right>
  <input name=remove type=checkbox> Remove
  <input type=submit value=Submit>
</td></tr>
</table>
</form>
</center>
_edit_
}

byebye() {
	echo "</html>"
	exit 0
}

cat << _header_
<div style="width:100%">
<table width=100%>
<tr><td><a href=Main>wk</a> ${PATH_INFO}</td>
<td align=right>
 <a href="?list">list</a>
 <a href="?search">search</a>
 <a href="?blog">blog</a>
 <a href="?">view</a>
 <a href="?edit">edit</a>
</td></tr></table>
</div>
<br />
_header_

do_save() {
	
	if [ `echo ${TEXT} | grep "remove"` ]; then
		if [ -f "${WKDB}/${PATH_INFO}" ]; then
			echo "<a href=Main>Removed</a>"
			rm -f "${WKDB}/${PATH_INFO}"
		else
			echo "Page does not exist"
		fi
	else
		echo "<a href=${PATH_INFO}>Saved</a>"
		echo $1 | cut -d '&' -f 1 | cut -d '=' -f 2 | urldecode > ${WKDB}/${PATH_INFO}
	fi
}


# Show left menu bar
echo "<table width=100%><tr><td class=menubar valign=top>"
if [ -f "${WKDB}/MenuBar" ]; then
	wikilinks "${WKDB}/MenuBar"
else
	echo "<a href=MenuBar?edit>edit MenuBar</a>"
fi
echo "</td><td valign=top width=85%>"


case "${QUERY_STRING}" in
"list")
	echo "<h2>Entries</h2>"
	cd ${WKDB} && ls | sort | perl -ne 'print "<a href=$_>$_</a><br />";'
	;;
"search")
	echo "<form action=?search method=post>" 
  	echo "Find: <input name=keyword style='width:200px'>"
  	echo "<input type=submit value=Submit>"
	echo "</form>"
	if [ "${REQUEST_METHOD}" = "POST" ]; then
		KEYWORD=`cat - | cut -d = -f 2`
		echo "<table width=100%>"
		cd db && grep -i -re ${KEYWORD} * | perl -ne '$a=$_;/([^:]*):(.*)$/; print "<tr><td><a href=$1>$1</a></td><td>$2</td></tr>"'
		echo "</table>"
	fi
	;;
"blog")
	FILES=`cd db && ls -t Blog.* 2>/dev/null`
	echo "<h2>Blog</h2>"
	for a in $FILES; do
		echo "<br/><br /><a href=$a>$a</a><br />"
		perl -e "\$a=\"${WKDB}/$a\";" -e 'local($sec,$min,$hr,$day,$mon,$yr,$wday,@dntcare) = localtime((stat("$a"))[9]); print ($yr+1900); print "-$mon-$day $hr:$min:$sec<hr />";'
		wikilinks "${WKDB}/$a"
		echo "<br /><br />"
	done
	;;
"save")
	if [ "${REQUEST_METHOD}" = "POST" ]; then
		TEXT=`cat -`
		if [ -z "${PASS}" ]; then
			do_save
		else
			if [ `echo ${TEXT} | grep "pass=${PASS}"` ]; then
				do_save "${TEXT}"
			else
				echo Invalid password
			fi
		fi
	else
		echo Oops
		show_vars
	fi
	byebye
	;;
"edit")
	do_edit
	;;
*)
	if [ -f "${WKDB}/${PATH_INFO}" ]; then
		wikilinks "${WKDB}/${PATH_INFO}"
	else 
		do_edit
	fi
esac

echo "</td></tr></table>"
byebye
-->
