#!/usr/bin/env python3
from pwn import *

context.log_level = "debug"
from sage.all import GF, EllipticCurve, inverse_mod, ceil, sqrt, floor
from tqdm import tqdm
import secrets

# P-256
p = 0xFFFFFFFF00000001000000000000000000000000FFFFFFFFFFFFFFFFFFFFFFFF
K = GF(p)
a = K(0xFFFFFFFF00000001000000000000000000000000FFFFFFFFFFFFFFFFFFFFFFFC)
b = K(0x5AC635D8AA3A93E7B3EBBD55769886BC651D06B0CC53B0F63BCE3C3E27D2604B)
E = EllipticCurve(K, (a, b))
G = E(
    0x6B17D1F2E12C4247F8BCE6E563A440F277037D812DEB33A0F4A13945D898C296,
    0x4FE342E2FE1A7F9B8EE7EB4A7C0F9E162BCE33576B315ECECBB6406837BF51F5,
)
order = 0xFFFFFFFF00000000FFFFFFFFFFFFFFFFBCE6FAADA7179E84F3B9CAC2FC632551 * 0x1
E.set_order(order)


def paillier_decrypt(c, l, m, n):
    x = pow(c, l, n**2) - 1
    pt = ((x // n) * m) % n
    return pt


tbl = {}
max_m = 0


def bsgs(G, h, M):
    global tbl, max_m
    m = ceil(sqrt(M))

    R = max_m * G
    for j in tqdm(range(max_m, m)):
        tbl[R] = j
        R += G
    max_m = m

    neg_mG = -m * G

    S = h
    for i in tqdm(range(m)):
        if S in tbl:
            return i * m + tbl[S]
        S += neg_mG

    return None  # not found


def solve():
    conn = connect("localhost", 1337)
    # conn = process(["python", "../src/chal.py"])
    conn.recvline()  # banner

    # ec public
    eck = eval(conn.recvline_startswith(b"public key:").decode().split(":", 1)[-1])
    B = E(eck["x"], eck["y"])

    # paillier
    paillier = eval(
        conn.recvline_startswith(b"paillier key:").decode().split(":", 1)[-1]
    )
    p, q = paillier["p"], paillier["q"]
    n = p * q
    lam = (p - 1) * (q - 1)
    mu = inverse_mod(lam, n)

    MIN_BSGS = 43
    STEP_SIZE = pow(2, MIN_BSGS)
    LOW = 0
    HIGH = order
    i = 0
    while (HIGH - LOW).bit_length() >= MIN_BSGS:
        i += 1
        k = (pow(STEP_SIZE, i) * n) // order
        ciphertext = (pow(2, n, n**2) * pow(n + 1, k, n**2)) % n**2
        conn.sendlineafter("ciphertext:", str(ciphertext).encode())

        mta_response = eval(conn.recvline_startswith(b"mta").decode().split(":", 1)[-1])
        zk_schnorr = eval(conn.recvline_startswith(b"zk").decode().split(":", 1)[-1])
        B2 = E(zk_schnorr["beta_pub"]["x"], zk_schnorr["beta_pub"]["y"])
        alpha = paillier_decrypt(mta_response, lam, mu, n)

        H = (k * B + B2 - alpha * G) * inverse_mod(
            n, order
        )  # should be equal to sn * G for some s directly correlated with size of secret

        bsgs_low = max(floor((k * LOW) / n) - 1, 0)
        bsgs_high = min(ceil((k * HIGH) / n) + 1, order - 1)
        bsgs_range = bsgs_high - bsgs_low
        print("bsgs_range:", bsgs_range.bit_length())
        s = bsgs_low + bsgs(G, H - bsgs_low * G, bsgs_range)

        HIGH = ceil((s + 1) * n / k)
        LOW = floor((s - 1) * n / k)
        print("HIGH", HIGH)
        print("LOW", LOW)
        print("HIGH - LOW", (HIGH - LOW).bit_length())

    secret_calc = LOW + bsgs(G, B - LOW * G, HIGH - LOW)
    conn.sendlineafter("guess secret:", str(secret_calc))
    conn.recvall()
    print(f"solved after {i} iterations")


if __name__ == "__main__":
    solve()
