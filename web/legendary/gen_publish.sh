#!/bin/bash

mkdir -p publish
mv src/flag.txt flag.tmp.txt
echo "DUCTF{test}" > src/flag.txt
tar -czvf publish/src-$(basename "$PWD").tar.gz src
mv flag.tmp.txt src/flag.txt