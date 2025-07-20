#include <cstdint>
#include <cstdio>
#include <cassert>
#include <cwchar>

// generated
#include "helper_export.h"

// Callback structure definitions
typedef uint32_t (*GetCharCallback)(uint32_t index);
typedef const wchar_t *(*GetStringCallbackFn)(const wchar_t *, wchar_t *, int);
typedef uint32_t (*GetIntCallbackFn)(const wchar_t *);

// Callbacks structure
typedef struct Callbacks_t
{
    GetIntCallbackFn eval_int;
} Callbacks;

uint8_t g_State[8] = {0xcc, 0xcc, 0xcc, 0xcc, 0xcc, 0xcc, 0xcc, 0xcc};

// DJB2 hash function
uint32_t djb2_hash(const char *s, size_t len)
{
    uint32_t hash = 5381;
    while (len--)
    {
        /* hash = 33 * hash ^ s[i]; */
        hash += (hash << 5);
        hash ^= *s++;
    }
    return hash;
}

uint32_t djb2_hash_unicode(const wchar_t *s, size_t max_len)
{
    const wchar_t *limit = s + max_len;
    const wchar_t *pos = s;
    while (*pos != 0 && pos < limit)
    {
        pos++;
    }
    size_t len = pos - s;
    return djb2_hash((const char *)s, len * 2);
}

void ARC4(const char *key, uint32_t key_len, uint8_t *buffer, uint32_t buffer_len)
{
    uint8_t state[256];
    uint8_t t;
    uint32_t i, j;
    size_t pos;

    for (i = 0; i < 256; i++)
    {
        state[i] = i;
    }

    j = 0;
    for (i = 0; i < 256; i++)
    {
        j = (j + state[i] + key[i % key_len]) % 256;
        t = state[i];
        state[i] = state[j];
        state[j] = t;
    }

    for (pos = 0, i = 0, j = 0; pos < buffer_len; pos++)
    {
        i = (i + 1) % 256;
        j = (j + state[i]) % 256;

        // Swap S[i] and S[j]
        t = state[i];
        state[i] = state[j];
        state[j] = t;

        buffer[pos] = buffer[pos] ^ state[(state[i] + state[j]) % 256];
    }
}

// Exported functions
extern "C"
{

    uint32_t HELPER_EXPORT Decrypt(const char *key, uint32_t key_len, uint8_t *buffer, uint32_t buffer_len)
    {
        ARC4(key, key_len, buffer, buffer_len);
        return 3;
    }

    bool decrypt_string(const uint8_t *encrypted_string, size_t encrypted_string_len,
                        wchar_t *decrypted_string, const uint8_t *key, size_t key_len, uint32_t string_hash)
    {
        memcpy(decrypted_string, encrypted_string, encrypted_string_len);
        ARC4((const char *)key, key_len, (uint8_t *)decrypted_string, encrypted_string_len);
        uint32_t decrypted_hash = djb2_hash_unicode(decrypted_string, encrypted_string_len / 2);
#ifdef DEBUG
        printf("\ndecrypted_hash: 0x%x\n", decrypted_hash)
#endif // DEBUG
        return (decrypted_hash == string_hash);
    }

    // Test the first character of the password
    uint32_t HELPER_EXPORT Check1(const wchar_t *password)
    {
        uint32_t result = 1;

        if (((uint8_t)(password[0]) ^ 0x43) != 11)
        {
            result = 0;
        }

        g_State[0] = password[0] | 0x72;

        // if (result == 1)
        // {
        //     assert(password[0] == L'H');
        // }

        return result;
    }

    // Test characters 5-6 of the password
    uint32_t HELPER_EXPORT Check2(GetCharCallback get_char)
    {
        uint32_t result = 1;
        // Validates chars 5-6 "ph"
        uint8_t v = get_char(5+3) ^ g_State[0];
        if (v != 9)
        {
            result = 0;
        }

        v += get_char(6+3);
        if (v != 116)
        {
            result = 0;
        }

        g_State[1] = ~(v + 30);

        // if (result)
        // {
        //     assert(get_char(5+3) == 115);
        //     assert(get_char(6+3) == 107);
        // }

        return result;
    }

    // Test the numeric characters of the password
    uint32_t HELPER_EXPORT Check3(Callbacks *callbacks)
    {
        wchar_t password_key[16] = {0};

        // I hope the compiler doesn't optimise this!
        for (int i = 0; i < 8; i++)
        {
            if (i == 2 || i == 3)
            {
                password_key[i] = L'S';
            }
            else if (i == 4)
            {
                password_key[i] = password_key[i - 1] + 4;
            }
        }

        for (int i = 0; i < 8; i++)
        {
            char c = 0;
            switch (i)
            {
            case 0:
                c = (password_key[3] ^ 3) & 0xFF;
                break;
            case 1:
                c = (password_key[0] ^ 17) & 0xFF;
                break;
            case 5:
                c = (password_key[4] ^ 24) & 0xFF;
                break;
            case 6:
                c = (password_key[5] ^ 29) & 0xFF;
                break;
            case 7:
                c = (password_key[6] ^ 22) & 0xFF;
            default:
                break;
            }

            if (c != 0)
            {
                password_key[i] = c;
            }
        }

        // Copy password from global variable
        wchar_t result[64] = {0};
        for (int i = 0; i < 12; i++)
        {
            wchar_t expr[64] = {0};
            // ord(%s[%d])
            wchar_t fmt[] = {L'o', L'r', L'd', L'(', L'%', L's', L'[', L'%', L'd', L']', L')', 0};
            swprintf(expr, fmt, password_key, i);
            result[i] = callbacks->eval_int(expr);
        }

        uint8_t chars[4];
        chars[0] = (uint8_t)(result[7] & 0xFF);  // "1"
        chars[1] = (uint8_t)(result[8] & 0xFF);  // "1"
        chars[2] = (uint8_t)(result[11] & 0xFF); // "3"
        chars[3] = (uint8_t)(result[4] & 0xFF);  // "0"

        wchar_t buffer[512] = {0};
        wchar_t constraint[128] = {0};

        // TODO: obfuscate these strings?
        swprintf(buffer, L"%d + 2 == %d and %d == %d and (%d - %c) == %d ", chars[1], chars[2], chars[0], chars[1], chars[2], chars[3], chars[2]);

        for (int i = 0; i < 3; i++)
        {
            swprintf(constraint, L" and %d > 48 and %d < 57", chars[i], chars[i]);
            wcscat(buffer, constraint);
        }

        return callbacks->eval_int(buffer);
    }

    // Test the second last two characters of the password and characters 2-4
    uint32_t HELPER_EXPORT Check4(Callbacks *callbacks)
    {
        // Get characters 1, 2, and 3 from the password via callback
        wchar_t p1_expr[] = {L'o', L'r', L'd', L'(', L'P', L'A', L'S', L'S', L'W', L'O', L'R', L'D', L'[', L'1', L']', L')', 0};
        wchar_t p2_expr[] = {L'o', L'r', L'd', L'(', L'P', L'A', L'S', L'S', L'W', L'O', L'R', L'D', L'[', L'2', L']', L')', 0};
        wchar_t p3_expr[] = {L'o', L'r', L'd', L'(', L'P', L'A', L'S', L'S', L'W', L'O', L'R', L'D', L'[', L'3', L']', L')', 0};

        uint8_t p1 = (uint8_t)callbacks->eval_int(p1_expr);
        uint8_t p2 = (uint8_t)callbacks->eval_int(p2_expr);
        uint8_t p3 = (uint8_t)callbacks->eval_int(p3_expr);

        // "int(KEY[0:4])" encrypted with the first two bytes of the global state array
        const uint8_t int_key_4[] = {
            0xf2, 0x1e, 0x2a, 0xf4, 0x21, 0xef, 0xf7, 0x29, 0x1b, 0x8b, 0x96, 0x17, 0x78, 0x8b, 0x32, 0x90,
            0x87, 0xb4, 0x58, 0xb5, 0xe1, 0xed, 0xb9, 0x48, 0x3e, 0xd9};
        wchar_t get_key[64] = {0};
        if (!decrypt_string(int_key_4, sizeof(int_key_4), get_key, g_State, 2, 0x6293def8))
        {
            return 0;
        }

        int b = callbacks->eval_int(get_key); // 6859
        // assert(b == 6859);

        g_State[3] = ((b >> 3) & 0xFF) ^ 0x36;
        g_State[4] = p1;
        g_State[5] = p2;
        g_State[6] = p1 ^ p2 ^ p3 ^ 0x10;

        // assert(g_State[0] == 0x7a);
        // assert(g_State[1] == 0x6d);
        // assert(g_State[2] == 0xcc);
        // assert(g_State[3] == 0x6f);
        // assert(g_State[4] == 0x79);
        // assert(g_State[5] == 0x64);
        // assert(g_State[6] == 0x7f);
        // assert(g_State[7] == 0xcc);

        // ord(PASSWORD[9]) encrypted
        // https://gchq.github.io/CyberChef/#recipe=Encode_text('UTF-16LE%20(1200)')RC4(%7B'option':'Hex','string':'7a6dcc6f79647fcc'%7D,'Latin1','Latin1')To_Hex('0x%20with%20comma',16)&input=b3JkKFBBU1NXT1JEWzldKQ
        const uint8_t get_password_nine_encrypted[] = {
            0xd0,0xe9,0xc1,0x5a,0x9e,0x0c,0x28,0x31,0x58,0x24,0x5d,0x68,0x54,0x8d,0x6f,0xe7,
            0xf6,0xdb,0xd7,0xe5,0xc0,0x4b,0x28,0x46,0xe7,0xa4,0x7e,0xcd,0x07,0xf8,0xf4,0x41
        };
        wchar_t get_password_nine[96] = {0};
        if (!decrypt_string(get_password_nine_encrypted, sizeof(get_password_nine_encrypted), get_password_nine, g_State, 8, 0x69fa99d))
        {
            return 0;
        }

        wchar_t n = callbacks->eval_int(get_password_nine);
        // assert(n == 'n');

        // Build string "int(KEY[11:13])""
        memmove(get_key + 13, get_key + 11, 4);
        get_key[8] = L'1';
        get_key[9] = get_key[8];
        get_key[10] = L':';
        get_key[11] = get_key[8];
        get_key[12] = get_key[8];
        get_key[12]++;
        get_key[12]++;

        if ((n ^ (b & 100)) != callbacks->eval_int(get_key))
        {
            return 0;
        }

        // Build string "ord(PASSWORD[10])" from string ord(PASSWORD[9])
        get_password_nine[13] -= 8;
        get_password_nine[14] = get_password_nine[13] - 1;
        get_password_nine[15] = get_key[13];
        get_password_nine[16] = get_key[14];
        wchar_t a = callbacks->eval_int(get_password_nine);

        // "int(KEY[0:2], 16)"
        const uint8_t int_key_0_2_hex_encrypted[] = {
            0xd6,0xe9,0xdd,0x5a,0x8e,0x0c,0x28,0x31,0x43,0x24,0x59,0x68,0x5e,0x8d,0x67,0xe7,
            0x91,0xdb,0xa2,0xe5,0xa0,0x4b,0x31,0x46,0x90,0xa4,0x67,0xcd,0x6b,0xf8,0xeb,0x41,
            0x20,0x94
        };
        wchar_t int_key_0_2_hex[64] = {0};

        if (!decrypt_string(int_key_0_2_hex_encrypted, sizeof(int_key_0_2_hex_encrypted), int_key_0_2_hex, g_State, 8, 0xa7d53695))
        {
            return 0;
        }

        // assert(a == 'a');
        if (a != callbacks->eval_int(int_key_0_2_hex) - 7)
        {
            return 0;
        }

        return 1;
    }

} // extern "C"
