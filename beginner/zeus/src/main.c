#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <stdint.h>

void xor(char *data, const char *key) {
    size_t len = 51;
    size_t key_len = 13;
    for (size_t i = 0; i < len; i++) {
        data[i] ^= key[i % key_len];
    }
}

int main(int argc, char *argv[]) {
    const char *expected_phrase = "To Zeus Maimaktes, Zeus who comes when the north wind blows, we offer our praise, we make you welcome!";
    const char *key = "Maimaktes1337";

    uint8_t encrypted_flag[] = {
        0x09,0x34,0x2a,0x39,0x27,0x10,0x1f,0x0c,0x1d,0x56,0x6c,0x5c,0x51,0x12,0x15,0x01,0x08,0x3e,0x04,0x18,0x1c,0x1e,0x41,0x5a,0x52,0x59,0x12,0x06,0x06,0x09,0x12,0x34,0x15,0x0b,0x17,0x6e,0x54,0x5c,0x53,0x12,0x0e,0x0f,0x32,0x15,0x03,0x11,0x3a,0x00,0x5a,0x4a,0x4e
    };

    if (argc == 3 &&
        strcmp(argv[1], "-invocation") == 0 &&
        strcmp(argv[2], expected_phrase) == 0) {
        
        printf("Zeus responds to your invocation!\n");
        char decrypted_flag[sizeof(encrypted_flag)];
        memcpy(decrypted_flag, encrypted_flag, sizeof(encrypted_flag));
        xor(decrypted_flag, key);
        printf("His reply: %s\n", decrypted_flag);

    } else {
        printf("The northern winds are silent...\n");
    }

    return 0;
}