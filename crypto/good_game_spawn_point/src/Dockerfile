FROM ghcr.io/downunderctf/docker-vendor/nsjail:ubuntu-24.04

RUN pip install -t /lib/python3/dist-packages pycryptodome

ENV TIME_LIMIT=1800
ENV CPU_SHARES_MS=300
ENV FLAG=DUCTF{g00d_gam3_5pawnling_533_y0u_in_th3_n3xt_chall3ng3}

COPY ./chal.py /home/ctf/chal/pwn
RUN chmod +x /home/ctf/chal/pwn
