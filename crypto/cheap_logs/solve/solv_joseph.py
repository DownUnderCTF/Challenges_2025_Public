from pwn import *
from tqdm import tqdm
from gmpy2 import mpz

"""
Bug: in init, free(buf) is called unconditionally. buf is the backing store for
priv's limbs. In print_public_key, when mpz_powm_sec is called, pub's limbs are
allocated and the free'd chunk from priv's limbs are reclaimed for this. This
means pub->_mp_d and priv->_mp_d are overlapping. This is why printing the
public key many times just after connecting will result in a different result
each time.

Also note, priv is set to be 0x111 * 64 bits long (even though p is only 0x11 * 64 bits)
The allocation made for pub->_mp_d matches the size of the modulus p, so enough
space for 0x11 limbs is allocated. This will form the bottom 1088 bits of the
privkey. Also note the first time that print_public_key is called and
pub->_mp_d reclaims some of the free'd priv->_mp_d chunk, the 40 bytes
following the 0x11 * 8 chunk for pub->_mp_d will be filled with free chunk
metadata: an unsorted bin chunk containing [0x801 | fd | bk | 0 | 0].
The remaining 251 limbs remain in tact.

So each time we print_public_key, we have
    priv =  2^(22 * sizeof(limb)) * random_251_limbs
          + 2^(17 * sizeof(limb)) * free_chunk_metadata
          + pub_prev
    pub = g^priv (mod p)
We know the bottom pub_prev part since we are given it in the previous call to
print_public_key.

Suppose we take the random/unknown part of the priv key mod q and call it X. So
    X = 2^(22 * sizeof(limb)) * random_251_limbs + 2^(17 * sizeof(limb)) * free_chunk_metadata (mod q)
Then
    priv = X + pub_prev
    pub = g^priv (mod p)
X is the same in each call to print_public_key, but pub_prev will change each time.
So we essentially have
    pub_i = g^(X + pub_{i-1}) (mod p)
can we recover X from this?
    pub_i = g^X g^(pub_{i-1}) (mod p)

But I think solving this would still require dlog. So let's look for another bug.

In submit_answer, mpz_inp_str is called to read in a hex string from stdin into
the mpz_t guess variable. This must do some allocation for guess->_mp_d, so it
should reclaim the rest of the chunk that makes up priv->_mp_d if chosen correctly!
Looking at the implementation of mpz_inp_str we can see that it dynamically
allocates heap space for reading in the string itself, and then allocates space
for the limbs of the number. The allocations for the string start at 100 bytes
and then increase by a multiple of 3/2 each time the buffer is filled. This
gives the discrete allocations of (ignoring chunk size rounding):
    0x64
    0x96
    0xe1
    0x151
    0x1f9
    0x2f5
    0x46f
    0x6a6
    0x9f9
achieved by sending a string of size less than or equal to the given bucket.
The free chunk overlapping the priv->_mp_d is of size 0x800 and we want to fill
this as much as possible with the str and the guess->_mp_d allocations.
Note that any subsequent call to submit_answer will have the same behaviour for
the string, but the guess->_mp_d will be realloc'd.
The allocation made for the limbs is 8 * (ceil(l * 4 / 64) + 2) bytes.
So we want to choose an l such that the allocation from the string plus the
allocation from the limbs covers the 0x800 free chunk as much as possible.
When l is between 0x361*2 and 0x370*2 inclusive, the chunk size is 0x380. So
sending a string of size between 0x361*2 and 0x370*2 will cause a 0x480 chunk
to be allocated for the string, breaking up the 0x800 region and putting the
remaining 0x380 chunk into the tcache, which is subsequently reclaimed for the
limbs to perfectly cover the full 0x800 chunk.

The layout of priv->_mp_d is now something like this:
    0x55ad821163f0: 0x77cc04d766d6e059      0x4760af9369b6ccbc <-+
    0x55ad82116400: 0xba0d556ac9e94c36      0x5fa5787bbc35f692   |
    0x55ad82116410: 0x0a399ae7efc13922      0x74b555060d56812c   |
    0x55ad82116420: 0x76dd12eaa6f3cab7      0xa8d57cc032f98408   |
    0x55ad82116430: 0xd7935b909e591e1b      0x7422ddc45d78ca5f   | pubkey limbs
    0x55ad82116440: 0x02715caf2cec47b0      0x0f05f12c6743c656   |
    0x55ad82116450: 0xf0834e31bcb82a5e      0xf8b7eb44d561105a   |
    0x55ad82116460: 0x1c2e80626ceb42bf      0x558ad7c22130b662   |
    0x55ad82116470: 0xbb38ac35f54a0aa4      0x0000000000000481 <-+ chunk metadata
    0x55ad82116480: 0x00007fd921e03b20      0x00007fd921e03b20 <-- unsorted bin free chunk fd/bk ptrs
    0x55ad82116490: 0x0000000000000000      0x0000000000000000
    0x55ad821164a0: 0x0f0f0f0f0f0f0f0f      0x0f0f0f0f0f0f0f0f <-+
        ...                                                      | 0x448 bytes of 0x0f
    0x55ad821168e0: 0x0f0f0f0f0f0f0f0f      0xfe0f0f0f0f0f0f0f <-+ (and a random byte)
    0x55ad821168f0: 0x0000000000000480      0x0000000000000380 <-- chunk metadata
    0x55ad82116900: 0xbac158f0943a299d      0xa41071886c1fd073 <-+
    0x55ad82116910: 0x099a2480435a36a0      0xa7a082318b151cdf   |
    0x55ad82116920: 0x49b7f2d2e5a2769d      0xad7018a3d113ad0a   |
    0x55ad82116930: 0x219ba0570a8ce757      0x05dccb81f97999ab   | guess limbs, equal to
    0x55ad82116940: 0xbf16893169321b29      0x6adf12d40bc12325   | g^(0xff...ff) (mod p)
    0x55ad82116950: 0xf5a97212efc2ef4a      0x2a4952b428a4078c   |      ^-----^
    0x55ad82116960: 0x787b8c01f0c2e349      0xc8de57334ff4e49a   |      1760 f's
    0x55ad82116970: 0xd15321519584fa7e      0xc895ac263ff5bbda   |
    0x55ad82116980: 0x76287054af9b227e      0xffffffffffffffff <-+
    0x55ad82116990: 0xffffffffffffffff      0xffffffffffffffff <-+
        ...                                                      | 0x2e0 bytes of 0xff
    0x55ad82116c60: 0xffffffffffffffff      0xffffffffffffffff <-+
    0x55ad82116c70: 0x0000000000000500

The only unknown parts are the two libc pointers, but they're both the same
value and have only 28 bits of entropy, so can be easily solved with BSGS/MITM.
There is also one extra byte of unknown randomness since the alloc size for the
string before it gets realloc'd is 0x46f (and the buffer is 0x470).
The libc address (in our example) is 0x00007fd921e03b20 which actually only has
around 28 bits of entropy:
    11111111101100100100001111000000011101100100000
    ^------^^---------------------------^---------^
     fixed      ASLR entropy               fixed

Algebraically, the private key's value at this point is:
      Y + 2^(1279 * 8) * b + 2^(144 * 8) * libc_ptr + 2^(152 * 8) * libc_ptr + pub_prev
    = Y + 2^(1279 * 8) * b + (2^(144 * 8) + 2^(152 * 8)) * libc_ptr + pub_prev
where Y is the fixed constant encompassing all the ff's, 0f's, guess limbs and
known chunk metadata values which we can easily obtain from a debugger.
Furthermore, we can write
    libc_ptr = 0x7f8000000320 + 2^11 * a
where a is the 28 bits of entropy
So
    priv_key = Y + 2^(1279 * 8) * b + (2^(144 * 8) + 2^(152 * 8)) * (0x7f8000000320 + 2^11 * a) + pub_prev
and we are given
    pub = g^priv_key (mod p)
        = g^Y g^(2^(1279 * 8) * b) g^((2^(144 * 8) + 2^(152 * 8)) * 0x7f8000000320) g^((2^(144 * 8) + 2^(152 * 8)) * 2^11 * a) g^pub_prev (mod p)
so
    pub / (g^Y g^(2^(1279 * 8) * b) g^((2(144 * 8) + 2^(152 * 8)) * 0x7f8000000320) g^pub_prev) =  (g^((2^(144 * 8) + 2^(152 * 8)) * 2^11))^a (mod p)
    pub / (g^Y g^(2^(1279 * 8) * b) g^((2(144 * 8) + 2^(152 * 8)) * 0x7f8000000320) g^pub_prev) =  base^a (mod p)
        where base = g^((2^(144 * 8) + 2^(152 * 8)) * 2^11)
There is a total of 36 bits that we need to recover, so we need to use a MITM approach.
We can write a = a_low + 2^10 a_high with a_low ~ 10 bits and a_high ~ 18 bits.
    pub / (g^Y g^(2^(1279 * 8) * b) g^((2(144 * 8) + 2^(152 * 8)) * 0x7f8000000320) g^pub_prev base^a_low) = (base^(2^10))^a_high (mod p)
This gives 8+10 = 18 bits for building the lookup table (b and a_low), and then 18 bits for the search (a_high).
"""

exe = ELF("../src/chall")

# conn = process([exe.path])
conn = remote("0.0.0.0", 1337)

conn.sendlineafter(b"> \n", b"3")
conn.sendlineafter(b"(hex): \n", 0x370 * 2 * b"f")

conn.sendlineafter(b"> \n", b"1")
conn.recvuntil(b"Public Key: ")
pub_prev = int(conn.recvline().decode(), 16)

conn.sendlineafter(b"> \n", b"1")
conn.recvuntil(b"Public Key: ")
pub = int(conn.recvline().decode(), 16)

p = 0xC2F2E0F7EC137C1F4F67D5B4276756FCDA5D5DAADDE9993AD2289D7CA855F50BCEC64FE5859C503A654F32422C5C02B5083BC83DB66EECBD347B971C0ACEF5A387C5E90FCFD25F87F565752574CC4D72E1AFE0E09A1FBFDE1F1960A56226523BD67B0E7FDE83FE53F85AC61D94AB52D837CCC1120F22D58CA79334E23B66AD23B1CB493F5DC8E2B7
g = mpz(2)
Y = 0x500FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF76287054AF9B227EC895AC263FF5BBDAD15321519584FA7EC8DE57334FF4E49A787B8C01F0C2E3492A4952B428A4078CF5A97212EFC2EF4A6ADF12D40BC12325BF16893169321B2905DCCB81F97999AB219BA0570A8CE757AD7018A3D113AD0A49B7F2D2E5A2769DA7A082318B151CDF099A2480435A36A0A41071886C1FD073BAC158F0943A299D00000000000003800000000000000480000F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0000000000000000000000000000000000000000000000000000000000000000000000000000048100000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000

lhs_lookup = {}
base = mpz(pow(g, ((2 ** (144 * 8) + 2 ** (152 * 8)) * 2**11), p))
lhs_base = (
    pub
    * pow(
        pow(g, Y, p)
        * pow(g, (2 ** (144 * 8) + 2 ** (152 * 8)) * 0x7F8000000320, p)
        * pow(g, pub_prev, p),
        -1,
        p,
    )
    % p
)
for b in tqdm(range(256)):
    lhs_base_b = lhs_base * pow(g, -(2 ** (1279 * 8)) * b, p) % p
    for a_low in range(2**10):
        lhs = lhs_base_b * pow(base, -a_low, p) % p
        lhs_lookup[lhs] = (b, a_low)

rhs_base = pow(base, 2**10, p)
rhs = 1
priv_key = None
for a_high in tqdm(range(1, 2**18)):
    rhs *= rhs_base
    rhs %= p
    if rhs in lhs_lookup:
        b, a_low = lhs_lookup[rhs]
        a = a_low + 2**10 * a_high
        priv_key = (
            Y
            + 2 ** (1279 * 8) * b
            + (2 ** (144 * 8) + 2 ** (152 * 8)) * (0x7F8000000320 + 2**11 * a)
            + pub_prev
        )
        print("found!", a_low, a_high, b)
        break
assert priv_key

conn.sendlineafter(b"> \n", b"3")
conn.sendlineafter(b"(hex): \n", hex(priv_key)[2:].encode())

conn.interactive()
