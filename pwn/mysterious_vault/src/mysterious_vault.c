#include <stdio.h>
#include <sys/wait.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/shm.h>
#include <openssl/sha.h>
#include <string.h>
#include <time.h>

unsigned char raw_hash[SHA256_DIGEST_LENGTH];
unsigned char hash[0x65];

#define CORRECT_PASSPHRASE "\x31\xd2\x48\x8d\x35\x1c\x00\x00\x00\x80\xfa\x1b\x7d\x0a\x80\x36\x42\xfe\xc2\x48\xff\xc6\xeb\xf1\xbf\x01\x00\x00\x00\x48\x29\xd6\x89\xf8\x0f\x05\xc3\x1b\x2d\x37\x62\x24\x2d\x37\x2c\x26\x62\x36\x2a\x27\x62\x27\x23\x31\x36\x27\x30\x62\x27\x25\x25\x62\x78\x6b"

#define PASS_LEN 0x40
#define BUFSZ 0x200
#define SHARED_ADDR 0x1337000


void setup() {
	setvbuf(stdout, NULL, _IONBF, 0);
	setvbuf(stderr, NULL, _IONBF, 0);

	int shmid = shmget(0xdeadbeef, 0x20, IPC_CREAT);
	if (shmid < 0) {
		fprintf(stderr, "ERROR. CRITICAL ERROR FOR `shmget`. PLEASE CONTACT ADMINISTRATIVE ENTITIES\n");
		exit(1);
	}

	void* res = shmat(shmid, (char*)SHARED_ADDR, 0);
	if (res == (void*)-1) {
		fprintf(stderr, "ERROR. CRITICAL ERROR FOR `shmid`. PLEASE CONTACT ADMINISTRATIVE ENTITIES\n");
		exit(1);
	}
}

void spawn_checkers() {
	if (fork() == 0) {
		puts("SPAWNING CHECKER 0x1");

		if (chroot("./checker1-trusted-env")) {
			fprintf(stderr, "ERROR. CRITICAL ERROR FOR `chroot`. PLEASE CONTACT ADMINISTRATIVE ENTITIES\n");
			exit(1);
		}

		if (execve("password_handler_3000", NULL, NULL)) {
			fprintf(stderr, "ERROR. CRITICAL ERROR FOR `execve`. PLEASE CONTACT ADMINISTRATIVE ENTITIES\n");
			exit(1);
		}
	}

	if (fork() == 0) {
		puts("SPAWNING CHECKER 0x2");

		if (chroot("./checker2-trusted-env")) {
			fprintf(stderr, "ERROR. CRITICAL ERROR FOR `chroot`. PLEASE CONTACT ADMINISTRATIVE ENTITIES\n");
			exit(1);
		}

		if (execve("password_handler_3001", NULL, NULL)) {
			fprintf(stderr, "ERROR. CRITICAL ERROR FOR `execve`. PLEASE CONTACT ADMINISTRATIVE ENTITIES\n");
			exit(1);
		}
	}
}

void get_flag() {
	char flag_buf[0x100] = {0};
	FILE * flag = fopen("flag.txt", "r");

	if (flag == NULL) {
		printf("VAULT OPENING FAILED. PLEASE CONTACT ADMINISTRATIVE ENTITIES\n");
		exit(1);
	}

	int res = fread(flag_buf, 1, 0x100, flag);
	if (res < 0) {
		printf("VAULT OPENING FAILED. PLEASE CONTACT ADMINISTRATIVE ENTITIES\n");
		exit(1);
	}

	printf("%s\n", flag_buf);
}

int main() {
	char name[BUFSZ] = {0};
	char passwd[BUFSZ] = {0};
	size_t name_len = 0;
	size_t passwd_len = 0;

	setup();

	printf("ACCESS REQUIRED. ENTER USERNAME: ");
	name_len = read(0, name, BUFSZ-1);

	printf("ENTER PASSCODE: ");
	passwd_len = read(0, passwd, BUFSZ-1);

	*((int*)SHARED_ADDR) = 0;
	*((int*)(SHARED_ADDR+4)) = passwd_len;

	memcpy((char*)SHARED_ADDR+8, passwd, passwd_len);

	printf("AUTHENTICATING");
	for (int i = 0 ; i < 3 ; i++)
		sleep(1); printf(".");
	printf("\n");

	spawn_checkers();

	pid_t wpid = 0;
	int status = 0;
	while ((wpid = wait(&status)) > 0) {
		if (WIFEXITED(status)) {
			if (WEXITSTATUS(status) != 0) {
				printf("PASSWORD CHECKER HAS FAILED. THE VAULT SHALL REMAIN CLOSED.\n");
				exit(1);
			}
		}
		else {
			printf("PASSWORD CHECKER HAS FAILED. THE VAULT SHALL REMAIN CLOSED.\n");
			exit(1);
		}
	}

	if (!memcmp((char*)SHARED_ADDR, CORRECT_PASSPHRASE, PASS_LEN)) {
		printf("ACCESS GRANTED. THE VAULT SHALL BE OPENED.\n");
		get_flag();
	} else {
		printf("DENIED. THE VAULT SHALL REMAIN CLOSED FOR ALL OF ETERNITY.\n");
	}

	return 0;
}
