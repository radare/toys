DESTDIR?=
PREFIX?=/usr
PFX=${DESTDIR}/${PREFIX}

all:
	@echo This makefile will install 

install:
	@echo PREFIX=${PREFIX}
	@echo DESTDIR=${DESTDIR}
	cd linetools && ${MAKE} install
	cd dhosts && ${MAKE} install
	cp bin/* ${DESTDIR}/${PREFIX}/bin
	sed -e 's,tokipona-dictionary.txt,${PREFIX}/share/doc/tokipona/tokipona-dictionary.txt,g' \
		< tokipona/toki > ${DESTDIR}/${PREFIX}/bin/toki
	chmod +x ${PFX}/bin/toki
	mkdir -p ${DESTDIR}/${PREFIX}/share/doc/tokipona
	cp tokipona/*.txt ${DESTDIR}/${PREFIX}/share/doc/tokipona
	-for a in /home/* ; do \
		[ -e $$a/.vimrc ] && cp vim/vimrc $$a/.vimrc ; \
	done
	@cat README
