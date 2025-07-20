FROM ghcr.io/downunderctf/docker-vendor/nsjail@sha256:e09057add76c4df3ac662a0f7233f788870efb50904074acadbbc44c2a0b0447

ENV FLAG=DUCTF{fr4gm3nt3d_d1scr3t3_fr4gm3nt5_l0g5_m4ss_h34p_m4554g1ng_gr00m1ng}

COPY nsjail.cfg /home/ctf/
COPY ld-linux-x86-64.so.2 libc.so.6 libgmp.so.10 /home/ctf/chal/
COPY chall /home/ctf/chal/pwn
RUN chmod +x /home/ctf/chal/pwn
