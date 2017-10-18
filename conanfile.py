import os
from conans import ConanFile, CMake, tools
from conans.util import files


class LibrdkafkaConan(ConanFile):
    name = "librdkafka"
    version = "0.11.0"
    license = "BSD 2-Clause"
    url = "https://github.com/ess-dmsc/conan-librdkafka"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    build_requires = "cmake_installer/1.0@conan/stable"
    default_options = "shared=False", "cmake_installer:version=3.9.0"

    def source(self):
        tools.download(
            "https://github.com/edenhill/librdkafka/archive/v0.11.0.tar.gz",
            "librdkafka-0.11.0.tar.gz"
        )
        tools.check_sha256(
            "librdkafka-0.11.0.tar.gz",
            "d4baf9a0d08767128913bb4e39d68995a95d7efa834fcf3e4f60c3156003b887"
        )
        tools.unzip("librdkafka-0.11.0.tar.gz")
        os.unlink("librdkafka-0.11.0.tar.gz")

    def build(self):
        files.mkdir("./librdkafka-0.11.0/build")
        with tools.chdir("./librdkafka-0.11.0/build"):
            cmake = CMake(self)

            cmake.definitions["RDKAFKA_BUILD_EXAMPLES"] = "OFF"
            cmake.definitions["RDKAFKA_BUILD_TESTS"] = "OFF"
            cmake.definitions["WITH_LIBDL"] = "OFF"
            cmake.definitions["WITH_PLUGINS"] = "OFF"
            cmake.definitions["WITH_SASL"] = "OFF"
            cmake.definitions["WITH_SSL"] = "OFF"
            cmake.definitions["WITH_ZLIB"] = "OFF"
            if tools.os_info.is_macos and self.options.shared:
                cmake.definitions["CMAKE_SKIP_RPATH"] = "TRUE"

            if self.settings.build_type == "Debug":
                cmake.definitions["WITHOUT_OPTIMIZATION"] = "ON"
            if self.options.shared:
                cmake.definitions["BUILD_SHARED_LIBS"] = "TRUE"

            cmake.configure(source_dir="..", build_dir=".")
            cmake.build(build_dir=".")

    def package(self):
        self.copy("rdkafka.h", dst="include/librdkafka",
                  src="librdkafka-0.11.0/src")
        self.copy("rdkafkacpp.h", dst="include/librdkafka",
                  src="librdkafka-0.11.0/src-cpp")
        self.copy("*.a", dst="lib", keep_path=False)
        if tools.os_info.is_macos:
            self.copy("*.dylib*", dst="lib", keep_path=False)
        else:
            self.copy("*.so*", dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ["rdkafka", "rdkafka++"]
