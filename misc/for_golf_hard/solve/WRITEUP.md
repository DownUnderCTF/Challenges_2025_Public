# Forensics Golf

## Writeup

The hard part of this challenge is getting the total bytes received from the sever under 24kb. The image is not that large but with a block size of 4096 this only gives you 6 blocks you can read.

The good news is you can read small fragments from the server effectively and the blocks you need are...

1. The super block (which is only 1024 bytes)
2. The block descriptor (64 bytes)
3. The root directory inode (256 bytes)
4. The root directory (4096 bytes)
5. Three sub directories (4096+256 for the inode)
6. The flag (4096 bytes)

In total this is 22848 bytes. You can optimize this further though.

You can test this locally with `go run . -listen-nbd localhost:6723 -nbd-write-limit-per-client 24576` on the server and `python solve.py localhost 6723` for the client.