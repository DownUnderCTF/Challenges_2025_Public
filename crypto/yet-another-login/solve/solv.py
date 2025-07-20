from pwn import *
from Crypto.Util.number import bytes_to_long, long_to_bytes
from tqdm import tqdm
import hlextend

def ph_add(c, a):
    return int(c * pow(g, a, n**2) % n**2)

def ph_add_ct(c, c2):
    return int(c * c2 % n**2)

def ph_mul(c, k):
    return int(pow(c, k, n**2))

def oracle(msg, mac):
    conn.sendlineafter(b'> ', b'2')
    conn.sendlineafter(b'Token: ', (msg + b'|' + mac).hex().encode())
    o = conn.recvline().decode()
    return 'Welcome' in o

def get_token(username):
    conn.sendlineafter(b'> ', b'1')
    conn.sendlineafter(b'Username: ', username)
    return bytes_to_long(bytes.fromhex(conn.recvline().decode().split('Token: ')[1]).partition(b'|')[2])

# conn = process(['python3', './chall.py'])
conn = remote('0.0.0.0', 1337)
n = int(conn.recvline().decode())
g = n + 1

c = get_token(b'user')

rec_pt = 0
for i in tqdm(range(256)):
    w = ph_add_ct(c, ph_mul(ph_add(c, -rec_pt), 1 << (255 - i)))
    if not oracle(b'user=user', long_to_bytes(w)):
        rec_pt |= 1 << i

hle = hlextend.sha256()
ext = hle.extend(b'user=admin', b'user=user', 16, long_to_bytes(rec_pt).hex())
h = bytes.fromhex(hle.hexdigest())
mac = long_to_bytes(pow(g, bytes_to_long(h), n**2))
oracle(ext, mac)
print(conn.recvline().decode())
