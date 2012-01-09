F=t|5+t*2+((t&59))>>8&(t+t>>4)
F=t*5 & (t>>7)|t*3&(t*4>>10)
F=(t|(t>>9|t>>7))*t&(t>>11|t>>9)
F=t*(((t>>16)|(t>>6))&69&(t>>9))
F=(t>>7|t|t>>6)*10+4*(t&t>>13|t>>6)
F=(t*(((t>>12)|(t>>8))&(63&(t>>4))))

FLAGS=$(shell pkg-config --cflags --libs sdl)
all:
	#gcc o.c  -I /opt/local/include/SDL/ -L/opt/local/lib -lSDL
	gcc o.c -DF="${F}" $(FLAGS)
	#./a.out

S+="t*(t>>((t>>9|t>>8))&63&t>>4)"
S+="t|5+t*2+((t&59))>>8&(t+t>>4)"
S+="t*5&(t>>7)|t*3&(t*4>>10)"
S+="(t|(t>>9|t>>7))*t&(t>>11|t>>9)"
S+="t*(((t>>16)|(t>>6))&69&(t>>9))"
S+="(t>>7|t|t>>6)*10+4*(t&t>>13|t>>6)"
S+="(t*(((t>>12)|(t>>8))&(63&(t>>4))))"
S+="(t*(t>>5|t>>8))>>(t>>16)"
S+="t*((t>>9|t>>13)&25&t>>6)"
S+="t*((t>>11&t>>8&123&t>>3)"
tune:
	for a in ${S} ; do \
		${MAKE} all F="$$a" ; \
		./a.out 89600 ; \
	done
