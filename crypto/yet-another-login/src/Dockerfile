FROM ghcr.io/downunderctf/docker-vendor/nsjail:ubuntu-24.04

RUN pip install -t /lib/python3/dist-packages pycryptodome

ENV TIME_LIMIT=300
ENV FLAG=DUCTF{now_that_youve_logged_in_its_time_to_lock_in}

COPY chall.py /home/ctf/chal/pwn
