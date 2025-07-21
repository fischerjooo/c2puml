CC=gcc
CFLAGS=-Wall -Wextra -I.

SRCS=$(wildcard *.c)
OBJS=$(SRCS:.c=.o)

all: sample typedef_test

sample: sample.o math_utils.o geometry.o logger.o
	$(CC) $(CFLAGS) -o sample sample.o math_utils.o geometry.o logger.o

typedef_test: typedef_test.o math_utils.o geometry.o logger.o
	$(CC) $(CFLAGS) -o typedef_test typedef_test.o math_utils.o geometry.o logger.o

clean:
	rm -f *.o sample typedef_test