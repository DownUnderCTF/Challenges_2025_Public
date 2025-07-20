#!/usr/bin/env python3

import heapq
from itertools import islice
from sympy import primerange


def p_smooth_sequence(
    callback, p=7, n=1000
):  # generate all p-smooth numbers. copied from OEIS A002473
    (v, oldv, h, psmooth_primes) = (1, 0, [1], list(primerange(1, p + 1)))
    for _ in range(n):
        v = heapq.heappop(h)
        if v != oldv:
            callback(v)
            oldv = v
            for p in psmooth_primes:
                heapq.heappush(h, v * p)


def print_current_state(known):
    print(bytes([k if k else ord("?") for k in known]))


def print_missing_indices(known):
    print([i for i, k in enumerate(known) if not k])


def guess(known, index, guess_value, callback):
    known[index] = guess_value
    p_smooth_sequence(callback, p=index, n=1000)
    print_current_state(known)
    print_missing_indices(known)


def solve():
    ciphertexts = [
        bytes.fromhex(line)
        for line in open("output.txt").readlines()
        if line.strip().startswith("f3")
    ]
    flag_len = len(ciphertexts[0]) // 7

    known = [None] * len(ciphertexts[0])
    known[1] = ord("U")

    def callback(v, p=len(ciphertexts)):
        if v >= flag_len:
            return

        for p in primerange(1, p + 1):
            if v % p == 0:
                quo = v // p
                assert known[quo] is not None, f"Missing {quo}"
                known[v] = known[quo] ^ ciphertexts[0][quo] ^ ciphertexts[p - 1][quo]
                break

    p_smooth_sequence(callback, p=7, n=1000)
    print_current_state(known)
    print_missing_indices(known)

    # From here, we manually cribdrag / guess the next characters to occur at
    # prime indicies. Propagate the results of that guess, then print the result
    # to check our work.
    guess(known, 11, ord("u"), callback)
    guess(known, 13, ord("g"), callback)
    guess(known, 17, ord("l"), callback)
    guess(known, 19, ord("t"), callback)
    guess(known, 23, ord("_"), callback)
    guess(known, 29, ord("o"), callback)
    guess(known, 31, ord("h"), callback)
    guess(known, 37, ord("r"), callback)
    guess(known, 41, ord("l"), callback)
    guess(known, 43, ord("r"), callback)
    guess(known, 47, ord("w"), callback)
    guess(known, 53, ord("l"), callback)
    guess(known, 59, ord("y"), callback)
    guess(known, 61, ord("f"), callback)
    guess(known, 67, ord("f"), callback)

    known[0] = ord("D")
    print_current_state(known)


if __name__ == "__main__":
    solve()
