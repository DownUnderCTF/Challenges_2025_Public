#!/usr/bin/python3 -u

import subprocess
import tempfile
import base64
import sys

with tempfile.NamedTemporaryFile() as f:
    try:
        sz = int(input("How many *base64* bytes is your exploit? "))

        if sz > 2 ** 20:
            print("Too big");
            exit(1)

        print("Paste your exploit as base64: ")

        data = base64.b64decode(sys.stdin.buffer.read(sz))
        print(data.decode())

        f.write(data)
        f.flush()

        subprocess.check_call(['./d8', f.name])
    except:
        print('Something went wrong!')
