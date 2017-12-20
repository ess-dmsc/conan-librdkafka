project(PackageTest CXX)
cmake_minimum_required(VERSION 2.8.12)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(SKIP_RPATH)

find_package(Threads)
find_package(LibRDKafka)

add_executable(example example.cpp)
target_link_libraries(example
LibRDKafka
${CMAKE_THREAD_LIBS_INIT})
