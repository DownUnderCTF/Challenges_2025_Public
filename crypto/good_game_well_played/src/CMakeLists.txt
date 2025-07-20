cmake_minimum_required(VERSION 3.13)
project(good-game-well-played LANGUAGES C CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_EXTENSIONS OFF)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
set(CMAKE_BUILD_TYPE Debug)
set(CMAKE_CXX_FLAGS_DEBUG "-g -O0")
find_package(Boost REQUIRED COMPONENTS json)

add_subdirectory(mpc-lib)

add_executable(challenge
    challenge.cpp
)

target_link_libraries(challenge PUBLIC cosigner uuid Boost::json)
