FROM ghcr.io/downunderctf/docker-vendor/nsjail:ubuntu-24.04

RUN pip install -t /lib/python3/dist-packages pycryptodome

COPY cryptosecrets.py /home/ctf/chal/
COPY server.py /home/ctf/chal/pwn
