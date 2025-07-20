cmake_minimum_required(VERSION 3.25)

project(PythonCtypesChallenge)

find_package(Python COMPONENTS Interpreter)

include(GenerateExportHeader)
add_library(
    helper
    SHARED
    helper.cpp
)
target_include_directories(
    helper
    PRIVATE
    ${PROJECT_BINARY_DIR}
)
target_link_options(
    helper
    PRIVATE
    /PDBALTPATH:%_PDB%
)
generate_export_header(helper)

add_custom_command(
    TARGET helper
    POST_BUILD
    COMMAND ${CMAKE_CURRENT_SOURCE_DIR}/tools/ducible.exe $<TARGET_FILE:helper>
    COMMENT "Running Ducible on binary"
)

find_package(Python3 COMPONENTS Interpreter)
add_custom_command(
    TARGET helper
    POST_BUILD
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/package.py $<TARGET_FILE:helper> ${CMAKE_CURRENT_SOURCE_DIR}/chal.py ${CMAKE_CURRENT_BINARY_DIR}/handout.py
    COMMENT "Packaging DLL into Python handout"
)
