FROM ghcr.io/downunderctf/docker-vendor/nsjail:ubuntu-22.04

ENV FLAG=DUCTF{w0w_pailli3r_skip_sav3s_12_s3c0nds_0ff_th3_any_p3rc3nt_run}

COPY ./challenge /home/ctf/chal/pwn
COPY ./nsjail.cfg /home/ctf/
RUN mkdir /home/ctf/chal/lib/
COPY lib/libcosigner.so lib/libboost_json.so.1.81.0 /home/ctf/chal/lib/
