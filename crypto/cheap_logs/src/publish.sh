#!/usr/bin/env sh

cp Dockerfile Dockerfile.tmp
sed -i 's/DUCTF{.*}/DUCTF{test_flag}/' Dockerfile
tar -czf ../publish/publish.tar.gz build.sh chall chall.c ld-linux-x86-64.so.2 libc.so.6 libgmp.so.10 nsjail.cfg Dockerfile
mv Dockerfile.tmp Dockerfile
