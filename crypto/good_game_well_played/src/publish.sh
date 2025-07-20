#!/usr/bin/env sh


tar -czf ../publish/ggwp.tar.gz --transform='s,^,good-game-well-played/,' build.sh challenge challenge.cpp challenge.diff CMakeLists.txt Dockerfile.build include lib Makefile GETTING_STARTED.md
