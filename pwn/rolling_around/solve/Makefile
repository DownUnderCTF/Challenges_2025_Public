CC=gcc
LPE =lpe

BIN = bin/
INC = include/

CMP = -o $(BIN)exploit.bin -I $(INC) exploit.c bpf.c kmem_search.c

groovy: 
	$(CC) -DGROOVY -static $(CMP)

hirsute: 
	$(CC) -DHIRSUTE -static $(CMP)

clean:
	rm $(BIN)exploit.bin
