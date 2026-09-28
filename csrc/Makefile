CC?=gcc
CFLAGS?=-O2 -Wall
all: enum search_binary search_ext search_unique_3letter search_binary_context2 search_vardelete
enum: enum.c
	$(CC) $(CFLAGS) -o $@ $<
search_binary: search_binary.c
	$(CC) $(CFLAGS) -o $@ $<
search_ext: search_ext.c
	$(CC) $(CFLAGS) -o $@ $<
search_unique_3letter: search_unique_3letter.c
	$(CC) $(CFLAGS) -o $@ $<
search_binary_context2: search_binary_context2.c
	$(CC) $(CFLAGS) -o $@ $<
search_vardelete: search_vardelete.c
	$(CC) $(CFLAGS) -o $@ $<
clean:
	rm -f enum search_binary search_ext search_unique_3letter search_binary_context2 search_vardelete \
	      enum.exe search_binary.exe search_ext.exe search_unique_3letter.exe \
	      search_binary_context2.exe search_vardelete.exe *.o
