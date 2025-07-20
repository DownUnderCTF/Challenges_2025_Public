#!/usr/bin/env sh

gfortran main.f90 -fno-stack-protector -fno-backtrace -funsigned -g -o main -O0
patchelf --set-interpreter ./ld-linux-x86-64.so.2 --set-rpath . ./main
