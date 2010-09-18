#!/bin/sh
cleanup() {
	rm -f 8.out $objs
}
trap cleanup INT
8g $@ || exit $?
objs=`echo $@|sed -e s,\.go,.8,g`
8l -o 8.out $objs || exit $?
./8.out
cleanup
