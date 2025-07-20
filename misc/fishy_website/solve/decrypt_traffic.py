from pyshark import *
from binascii import unhexlify
from Crypto.Cipher import ARC4

SECRET = b"\xf1n\xcd\xc6yLf\xd1\x02\xf83\xc4\x86\xe7\xa45\x8di\xbd\xd2\x1dP\xf5\xfb\xdf\xec\xaf\x0b\x9eS\xa4\xd3"

packets = FileCapture("../publish/capture.pcapng", display_filter="ip.addr == 20.5.48.200 && tls.app_data")

for packet in packets:
    rc4 = ARC4.new(SECRET)
    packet_bytes = unhexlify(packet.tls.app_data.replace(":", ""))
    if packet.ip.dst == "20.5.48.200":
        packet_bytes = packet_bytes[:-4]
    payload = rc4.decrypt(packet_bytes).decode()
    if packet.ip.dst == "20.5.48.200":
        print(payload)
    else:
        print(f"> {payload}")
