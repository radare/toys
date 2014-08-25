#!/bin/sh

text='Éé'  # UTF-8; shows up as ÃÃ© on a latin1 terminal
dsr="\033[6n\033[5n"
#stty_save=`stty -g`

stty eol 0 eof n -echo                # Input will end with `0n`

printf "$dsr"              # Ask the terminal to report the cursor position
initial_report=`tr -dc \;0123456789 | cut -d ';' -f2`  # Expect ␛[42;10R␛[0n for y=42,x=10
printf "$text$dsr"
final_report=`tr -dc \;0123456789 |cut -d ';' -f2`

#stty "$stty_save"

DIFF=$(($final_report-$initial_report))
if [ "$DIFF" = 20 ]; then
	printf "\rUTF-8\n"
else
	printf "\rASCII\n"
fi
echo $DIFF
