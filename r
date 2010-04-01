#!/bin/sh
echo "\$ $*" | xsel -i
$* 2>&1 | tee .tmp.$$
cat .tmp.$$ | xsel -a -i
rm .tmp.$$
