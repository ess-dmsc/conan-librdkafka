import os
from conans import ConanFile, CMake, tools
from conans.util import files


class LibrdkafkaConan(ConanFile):
    name = "librdkafka"
    version = "0.11.1"
    license = "BSD 2-Clause"
    url = "https://github.com/ess-dmsc/conan-librdkafka"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    build_requires = "cmake_installer/1.0@conan/stable"
    default_options = "shared=False", "cmake_installer:version=3.9.0"

    def source(self):
        tools.download(
            "https://github.com/edenhill/librdkafka/archive/v0.11.1.tar.gz",
            "librdkafka-0.11.1.tar.gz"
        )
        tools.check_sha256(
            "librdkafka-0.11.1.tar.gz",
            "dd035d57c8f19b0b612dd6eefe6e5eebad76f506e302cccb7c2066f25a83585e"
        )
        tools.unzip("librdkafka-0.11.1.tar.gz")
        os.unlink("librdkafka-0.11.1.tar.gz")

    def build(self):
        files.mkdir("./librdkafka-0.11.1/build")
        with tools.chdir("./librdkafka-0.11.1/build"):
            cmake = CMake(self)

            cmake.definitions["RDKAFKA_BUILD_EXAMPLES"] = "OFF"
            cmake.definitions["RDKAFKA_BUILD_TESTS"] = "OFF"
            cmake.definitions["WITH_LIBDL"] = "OFF"
            cmake.definitions["WITH_PLUGINS"] = "OFF"
            cmake.definitions["WITH_SASL"] = "OFF"
            cmake.definitions["WITH_SSL"] = "OFF"
            cmake.definitions["WITH_ZLIB"] = "OFF"
            if tools.os_info.is_macos and self.options.shared:
                cmake.definitions["CMAKE_MACOSX_RPATH"] = "ON"

            if self.settings.build_type == "Debug":
                cmake.definitions["WITHOUT_OPTIMIZATION"] = "ON"
            if self.options.shared:
                cmake.definitions["BUILD_SHARED_LIBS"] = "ON"

            cmake.configure(source_dir="..", build_dir=".")
            cmake.build(build_dir=".")

            os.rename("../LICENSE", "LICENSE.librdkafka")

    def package(self):
        self.copy("rdkafka.h", dst="include/librdkafka",
                  src="librdkafka-0.11.1/src")
        self.copy("rdkafkacpp.h", dst="include/librdkafka",
                  src="librdkafka-0.11.1/src-cpp")
        self.copy("*.a", dst="lib", keep_path=False)
        if tools.os_info.is_macos:
            self.copy("*.dylib*", dst="lib", keep_path=False)
        else:
            self.copy("*.so*", dst="lib", keep_path=False)
        self.copy("LICENSE.*", src="librdkafka-0.11.1")

    def package_info(self):
        self.cpp_info.libs = ["rdkafka", "rdkafka++"]
