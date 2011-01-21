DESTDIR?=
PREFIX?=/usr

all:
	@echo This makefile will install 

install:
	cd linetools && ${MAKE} install
	cd dhosts && ${MAKE} install
	cp bin/* ${DESTDIR}/${PREFIX}/bin
	cp tokipona/toki ${DESTDIR}/${PREFIX}/bin
	mkdir -p ${DESTDIR}/${PREFIX}/share/doc/tokipona
	cp tokipona/*.txt ${DESTDIR}/${PREFIX}/share/doc/tokipona
	-for a in /home/* ; do \
		[ -e $$a/.vimrc ] && cp vim/vimrc $$a/.vimrc ; \
	done
	@cat README
