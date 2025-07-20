qemu-system-x86_64 \
    -m 256M \
    -smp 1 \
    -cpu qemu64,+smep,+smap \
    -kernel bzImage \
    -initrd rootfs.cpio.gz \
    -nographic \
    -monitor /dev/null \
    -no-reboot \
    -append "console=ttyS0 quiet kaslr kpti=1 pti=on panic=0 oops=panic"
