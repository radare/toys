#!/bin/sh

./list > db/list.tmp
[ -e db/list.tmp ] && mv db/list.tmp db/list
