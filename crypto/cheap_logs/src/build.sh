#!/usr/bin/env sh

# gcc -I. -L. -lgmp -Wl,--dynamic-linker=./ld-linux-x86-64.so.2,-rpath=. chall.c -o chall

# #!/bin/sh

build_script=$(mktemp)
echo '#!/bin/bash' >> $build_script
echo "cd /tmp/build" >> $build_script
echo "apt update -y" >> $build_script
echo "apt install -y gcc libgmp-dev patchelf" >> $build_script
echo "cp /lib/x86_64-linux-gnu/libgmp.so.10 ." >> $build_script
echo "gcc -o chall chall.c -lgmp" >> $build_script
echo "cp /lib/x86_64-linux-gnu/libc.so.6 /lib64/ld-linux-x86-64.so.2 ." >> $build_script
echo "patchelf --set-interpreter ./ld-linux-x86-64.so.2 --set-rpath . ./chall" >> $build_script
chmod +x $build_script

docker run -v$(pwd):/tmp/build -v"$build_script:/tmp/build/build.sh" ubuntu:latest "/tmp/build/build.sh"
