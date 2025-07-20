# Forensics Golf

## Writeup

The filesystem is exposed over a Network Block Device server. The flag is found in a similar location to the beginner challenge.

Using TinyRange (https://github.com/tinyrange/tinyrange): `tinyrange login nbd-client -E "nbd-client -N root <ip> <port> /dev/nbd0; sleep 1; mount /dev/nbd0 /mnt" -o /mnt/flag.jpg --rebuild`