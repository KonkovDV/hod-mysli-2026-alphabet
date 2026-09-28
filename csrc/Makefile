CC?=gcc
CFLAGS?=-O2 -Wall
all: enum search_binary search_ext
enum: enum.c
	$(CC) $(CFLAGS) -o $@ $<
search_binary: search_binary.c
	$(CC) $(CFLAGS) -o $@ $<
search_ext: search_ext.c
	$(CC) $(CFLAGS) -o $@ $<
clean:
	rm -f enum search_binary search_ext enum.exe search_binary.exe search_ext.exe *.o
