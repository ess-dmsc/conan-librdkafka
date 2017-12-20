project(PackageTest CXX)
cmake_minimum_required(VERSION 2.8.12)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(SKIP_RPATH)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
find_package(LibRDKafka)

find_package(Threads)

add_executable(example example.cpp)
target_link_libraries(
  example
  ${LibRDKafka_LIBRARIES}
  ${CMAKE_THREAD_LIBS_INIT}
)
