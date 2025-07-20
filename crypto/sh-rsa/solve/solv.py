from pwn import *
import sys
from Crypto.Util.number import long_to_bytes, bytes_to_long
from hashlib import shake_128
from tqdm import tqdm

def H(N, m):
    return shake_128(long_to_bytes(N) + m).digest(8)

HAS_POW = False
tries = 0
while True:
    rust_solver = process('./solv/target/release/solv', stderr=sys.stderr, level='error')

    # conn = process(['python3', './chal.py'], level='error')
    conn = remote('0.0.0.0', 1337)

    if HAS_POW:
        print(conn.recvuntil(b'Solution?').decode())
        sol = input('sol: ')
        conn.sendlineafter(b' ', sol.encode())
        print(conn.recvline().decode())

    N = int(conn.recvline().decode().split('N = ')[1])
    e = int(conn.recvline().decode().split('e = ')[1])
    T = bytes_to_long(H(N, b'challenge'))
    if T.bit_length() < 63:
        print('Try again (bad T)')
        rust_solver.close()
        conn.close()
        continue

    tries += 1

    print('Collecting data...')
    msg_hashes = []
    sigs = []
    for _ in tqdm(range(92)):
        m, s = conn.recvline().decode().split()
        msg_hashes.append(bytes_to_long(H(N, bytes.fromhex(m))))
        sigs.append(int(s, 16))

    ls = 23
    N = 4 * ls
    L1, L2, L3, L4 = [msg_hashes[i*(N//4):(i+1)*N//4] for i in range(4)]
    S1, S2, S3, S4 = [sigs[i*(N//4):(i+1)*N//4] for i in range(4)]

    rust_solver.sendline(hex(T)[2:].encode())
    for l in [L1, L2, L3, L4]:
        rust_solver.sendline(' '.join(map(str, l)).encode())

    try:
        sol_bitmap = int(rust_solver.recvline().decode())
        rust_solver.close()

        rs = 32 - ls
        S = S1 + [0] * rs + S2 + [0] * rs + S3 + [0] * rs + S4 + [0] * rs
        s = 1
        for i in range(128):
            if sol_bitmap & 1:
                s *= S[i]
            sol_bitmap >>= 1
        conn.sendlineafter(b's: ', hex(s).encode())
        print(conn.recvline().decode())

        print('Solved after', tries, 'tries')

        break
    except:
        rust_solver.close()
        conn.close()
        print('Try again (solver failed)')
