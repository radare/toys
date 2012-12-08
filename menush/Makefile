all:
	gcc eread.c -o eread -lreadline

install:
	cp eread /usr/bin/
	cp menush.sh /usr/bin/menush
	chmod +x /usr/bin/menush /usr/bin/eread

clean:
	rm -f eread

dist: clean
	cd .. && tar czvf menush.tar.gz menush
	scp ../menush.tar.gz foo@news.nopcode.org:/home/www/nopcode
