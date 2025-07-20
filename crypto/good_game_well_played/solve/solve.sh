#!/usr/bin/env sh

set -xe

if [[ ! -d "good-game-well-played" ]]; then
    cp ../publish/ggwp.tar.gz .
    tar -xzvf ggwp.tar.gz
fi

cp solve.cpp good-game-well-played/challenge.cpp
cp solve.diff good-game-well-played/challenge.diff

pushd good-game-well-played
GIT_PAGER=cat ./build.sh
socat EXEC:"./challenge client" tcp:localhost:1337
popd
