FROM ghcr.io/downunderctf/docker-vendor/nsjail:ubuntu-22.04

ENV MOUNT_PROC=false JAIL_CWD=/chal TMP_ENABLED=1 FLAG=./flag-48ab60a43ce3e021d245a7f3a92532db.txt
COPY nsjail.cfg /home/ctf/nsjail.cfg

COPY flag.txt /home/ctf/chal/flag-48ab60a43ce3e021d245a7f3a92532db.txt

COPY run.py /home/ctf/chal/pwn
COPY d8 /home/ctf/chal/d8
COPY snapshot_blob.bin /home/ctf/chal/snapshot_blob.bin
