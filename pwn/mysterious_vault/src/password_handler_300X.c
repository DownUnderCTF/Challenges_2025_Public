#include <stddef.h>
#include <stdio.h>
#include <unistd.h>
#include <string.h>
#include <stdlib.h>
#include <stdint.h>
#include <time.h>

#define IPC_CREAT 01000
#define PASSWD_LEN 0x20
#define SHARED_ADDR 0x1337000
#define SYS_shmget 29
#define SYS_shmat 30


#define SYS_seccomp 317

#define SCMP_ACT_KILL 0
#define SCMP_ACT_ALLOW 0x7fff0000U
#define SECCOMP_SET_MODE_STRICT  0

#define PR_SET_NO_NEW_PRIVS 38
#define PR_SET_SECCOMP 22
int prctl(int, ...);

struct sock_fprog {
	unsigned short len;
	void * filter;
};


void setup_sandbox() {
	char filter_bytes[] = "\x20\x00\x00\x00\x04\x00\x00\x00\x15\x00\x00\x08\x3e\x00\x00\xc0\x20\x00\x00\x00\x00\x00\x00\x00\x35\x00\x00\x01\x00\x00\x00\x40\x15\x00\x00\x05\xff\xff\xff\xff\x15\x00\x03\x00\x00\x00\x00\x00\x15\x00\x02\x00\x01\x00\x00\x00\x15\x00\x01\x00\x3c\x00\x00\x00\x15\x00\x00\x01\x02\x00\x00\x00\x06\x00\x00\x00\x00\x00\xff\x7f\x06\x00\x00\x00\x00\x00\x00\x00";
	struct sock_fprog prog = {       
		.len = 11,
		.filter = (struct sock_filter*)filter_bytes,
	};

	if (prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0)) {     
		fprintf(stderr, "ERROR. CRITICAL ERROR WHEN LOCKING DOWN CHECKER. PLEASE CONTACT ADMINISTRATIVE ENTITIES\n");
		exit(1);
	}   

	if (prctl(PR_SET_SECCOMP, 2, &prog)) {     
		fprintf(stderr, "ERROR. CRITICAL ERROR WHEN LOCKING DOWN CHECKER. PLEASE CONTACT ADMINISTRATIVE ENTITIES\n");
		exit(1);
	}
}

//Lockdown our password checker!!
void setup() {
	//Ensure chroot takes place
	chdir("/");

	int shm_id = syscall(SYS_shmget, 0xDEADBEEF, PASSWD_LEN, IPC_CREAT);
	if (shm_id < 0) {
		fprintf(stderr, "ERROR. CRITICAL ERROR FOR `shmget` IN CHECKER. PLEASE CONTACT ADMINISTRATIVE ENTITIES\n");
		exit(1);
	}

	void * ret = (void*)syscall(SYS_shmat, shm_id, (void*)SHARED_ADDR, 0);
	if (ret == (void*)-1) {
		fprintf(stderr, "ERROR. CRITICAL ERROR FOR `shmat` IN CHECKER. PLEASE CONTACT ADMINISTRATIVE ENTITIES\n");
		exit(1);
	}

	close(0); close(1); close(2);
	setup_sandbox();
}

int main() {
	setup();

	char password[200] = {0};
	int passwd_len = 0;

	passwd_len = *((int*)(SHARED_ADDR+4));
	memcpy(password, (char*)SHARED_ADDR+8, passwd_len);
	*((int*)SHARED_ADDR) += 1;

	//Synchronise
	while (*((volatile int*)SHARED_ADDR) != 2) {}

	if (strcspn(password, "password") != strlen(password)) {
		exit(1);
	}

	return 0;
}
