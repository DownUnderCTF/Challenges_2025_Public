#!/usr/bin/env bash
socat -dd TCP-LISTEN:1337,reuseaddr,fork EXEC:./certvalidated.py