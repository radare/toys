.PHONY: all install deb
PREFIX?=/usr
DESTDIR?=

all:

install:
	mkdir -p ${DESTDIR}/${PREFIX}/bin
	mkdir -p ${DESTDIR}/${PREFIX}/share/applications/
	chmod +x dhosts dhosts-update dhosts-sudo
	cp dhosts dhosts-update ${DESTDIR}/${PREFIX}/bin
	cp dhosts-sudo ${DESTDIR}/${PREFIX}/bin
	cp dhosts.desktop ${DESTDIR}/${PREFIX}/share/applications/

deb:
	rm -rf deb
	mkdir deb
	make install PREFIX=/usr DESTDIR=deb
	cd deb && tar czvf data.tar.gz *
	cd deb && find * -type f | xargs md5sum > md5sums
	cp control deb
	cd deb && tar czvf control.tar.gz md5sums control
	echo 2.0 > deb/debian-binary
	rm -f dhosts-0.1.deb
	cd deb && ar cqvf ../dhosts-0.1.deb debian-binary data.tar.gz control.tar.gz
	rm -rf deb
