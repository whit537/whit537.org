EXEC_NAME=return


all: clean
	gcc -ansi -pedantic -W -Wall -g -o ${EXEC_NAME} *.c

test: all
	./test.py

install:
	mv return ../../../bin/

default: all

clean:
	rm -f ${EXEC_NAME} *.a *.o output.txt gmon.out

