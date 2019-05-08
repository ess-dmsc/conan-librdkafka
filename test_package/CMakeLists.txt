project(PackageTest CXX)
cmake_minimum_required(VERSION 2.8.12)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(KEEP_RPATHS)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
find_package(LibRDKafka)

find_package(Threads)
find_package(ZLIB)

message(INFO "libc++ =  ${LibRDKafka_LIBRARIES}")
message(INFO "libc = ${LibRDKafka_C_LIBRARIES}")

add_executable(example example.cpp)
target_link_libraries(
  example
  ${LibRDKafka_LIBRARIES}
  ${LibRDKafka_C_LIBRARIES}
  ${CMAKE_THREAD_LIBS_INIT}
  ${ZLIB_LIBRARIES}
  ${CMAKE_DL_LIBS}
)
