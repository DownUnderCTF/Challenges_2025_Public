@echo off

cmake -S . -B build -G "Visual Studio 17 2022"
cmake --build build --config RelWithDebInfo
ctest --test-dir build -C RelWithDebInfo --output-on-failure
