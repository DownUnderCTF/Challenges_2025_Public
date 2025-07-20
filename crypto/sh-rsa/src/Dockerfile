FROM ghcr.io/downunderctf/docker-vendor/nsjail:ubuntu-24.04

RUN pip install -t /lib/python3/dist-packages pycryptodome gmpy2

ENV TIME_LIMIT=300
ENV CPU_SHARE_MS=500
ENV FLAG=DUCTF{how_did_you_break_64_bits_in_46_seconds!?}

COPY sh-rsa.py /home/ctf/chal/pwn
