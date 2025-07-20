FROM ghcr.io/downunderctf/docker-vendor/nsjail@sha256:e09057add76c4df3ac662a0f7233f788870efb50904074acadbbc44c2a0b0447

COPY nsjail.cfg /home/ctf/
COPY libm.so.6 ld-linux-x86-64.so.2 libc.so.6 libgfortran.so.5 libgcc_s.so.1 /home/ctf/chal/
COPY main /home/ctf/chal/pwn
COPY FLAG.TXT /home/ctf/chal/FLAG.TXT
RUN chmod +x /home/ctf/chal/pwn
