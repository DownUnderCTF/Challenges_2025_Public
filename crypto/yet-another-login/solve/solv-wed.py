#!/usr/bin/env python3

from pwn import *
from secrets import randbits
from Crypto.Util.number import *
import HashTools  # pip install length-extension-tool

context.log_level = "debug"

# This challenge is a variation on the classic hash length extension challenge,
# where the server produces MACs using a hash(secret + data) construction.
# However rather than receiving hash(secret + data) directly, we receive the
# Paillier encrypted ciphertext of hash(secret + data) So our goal is to reverse
# the encryption somehow, and then perform a length extension attack.

# Looking at the code, the verify function is a bit strange, because it only
# checks the least significant 256 bits of the decrypted plaintext. This means
# that both the tokens:
# - E(hash(secret + data))
# - E(2^256 hash(secret + data)) + E(hash(secret + data))
# are valid tokens for the message `data`. Furthermore since Paillier is
# homomorphic, we can generate both tokens from just knowledge of the public key
# and the value of E(hash(secret + data)), which we get from the registration
# functionality.
#
# Shifting the above approach by a bit, this means that we can also compute the
# value E(2^255 hash(secret + data) + hash(secret + data)). In this value, the
# MSB of hash(secret + data) overlaps with the LSB of hash(secret + data).

# If the LSB of hash(secret + data) is zero, then nothing changes in the least
# significant 256 bits, so verification proceeds as normal. On the other hand if
# the LSB of hash(secret + data) is set, then the 256th bit will be corrupted,
# leading to a verification failure.

# Distinguishing between the two cases gives us an oracle which tells us the LSB
# of hash(secret + data). By building on our partial knowledge of the LSBs, we
# can repeat the idea for all other bits too, which allows us to recover the
# full value of hash(secret + data). Once we know the full value, we can perform
# a length extension attack as normal.


def encrypt(n, g, m):
    n2 = n * n
    r = randbits(1024)
    c = pow(g, m, n2) * pow(r, n, n2) % n2
    return c


def register(conn, username):
    conn.sendlineafter(b"> ", "1")
    conn.sendlineafter(b"Username: ", username)
    return bytes.fromhex(
        conn.recvline_startswith(b"Token:").decode().split(":")[-1].strip()
    ).partition(b"|")


def login(conn, msg, mac):
    conn.sendlineafter(b"> ", "2")
    conn.sendlineafter(b"Token: ", b"|".join((msg, long_to_bytes(mac))).hex())
    return b"Failed to verify" not in conn.recvline()


def main():
    conn = connect("localhost", 1337)
    n = int(conn.recvline().decode())
    nsq = n * n
    g = n + 1

    A_msg, _, A_mac = register(conn, b"user1")
    A_mac = bytes_to_long(A_mac)

    # Step 1: Recover the original value of sha256(secret + user=user1) bit by
    # bit
    A_solved = 0
    for i, shift in enumerate(reversed(range(256))):
        A_zerolsb = (A_mac * encrypt(n, g, -A_solved)) % nsq
        to_test = (pow(A_zerolsb, pow(2, shift), nsq) * A_mac) % nsq
        if not login(conn, A_msg, to_test):
            A_solved += pow(2, i)
        print("A_solved:", bin(A_solved)[2:])

    # Step 2: Using knowledge of sha256(secret + user=user1), perform length
    # extension to forge a token
    magic = HashTools.new("sha256")
    new_msg, new_mac = magic.extension(
        secret_length=16,
        original_data=b"user=user1",
        append_data=b"user=admin",
        signature=long_to_bytes(A_solved).hex(),
    )
    assert new_msg.rpartition(b"user=")[2] == b"admin"
    new_mac = encrypt(n, g, int(new_mac, 16))
    login(conn, new_msg, new_mac)


if __name__ == "__main__":
    main()
