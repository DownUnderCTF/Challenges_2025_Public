#!/usr/bin/env sh

cp FLAG.TXT FLAG.TXT.bak
echo DUCTF{test_flag} > FLAG.TXT
tar -czf ../publish/publish.tar.gz Dockerfile build.sh ld-linux-x86-64.so.2 libc.so.6 libgcc_s.so.1 libgfortran.so.5 libm.so.6 main main.f90 nsjail.cfg FLAG.TXT
mv FLAG.TXT.bak FLAG.TXT
