#!/usr/bin/make -f
# $Id: Makefile,v 1.1.1.1 2003/10/21 17:56:45 jkohen Exp $
#
# This makefile provides simple rules to compile the assembly output of
# InlineEgg to native objects.
#
# It's been tailored for Linux, but it shouldn't be hard to add a couple
# more of rules for other systems.

## Linux + GCC
# ELF objects
.S:
	cc -o $@ $< -nostdlib -Xlinker -s -Xlinker --gc-sections
# A.out objects
#.S:
#	cc -c $< -nostdlib
#	ld -notstdlib --oformat a.out-i386-linux -static -s $@.o -o $@ -Ttext 0
