import os
from conans import ConanFile, CMake, tools
from conans.util import files


class LibrdkafkaConan(ConanFile):
    name = "librdkafka"
    sha256 = "2b96d7ed71470b0d0027bd9f0b6eb8fb68ed979f8092611c148771eb01abb72c"

    version = "0.11.3-dm1"
    license = "BSD 2-Clause"
    url = "https://github.com/ess-dmsc/conan-librdkafka"
    description = "The Apache Kafka C/C++ library"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = "shared=False"

    folder_name = "{}-{}".format(name, version)
    archive_name = "{}.tar.gz".format(folder_name)

    def source(self):
        tools.download(
            "https://github.com/edenhill/librdkafka/archive/v{}.tar.gz".format(self.version),
            self.archive_name
        )
        tools.check_sha256(
            self.archive_name,
            self.sha256
        )
        tools.unzip(self.archive_name)
        os.unlink(self.archive_name)

    def build(self):
        files.mkdir("./{}/build".format(self.folder_name))
        with tools.chdir("./{}/build".format(self.folder_name)):
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

            os.rename("../LICENSE", "../LICENSE.librdkafka")

    def package(self):
        self.copy("rdkafka.h", dst="include/librdkafka",
                  src="{}/src".format(self.folder_name))
        self.copy("rdkafkacpp.h", dst="include/librdkafka",
                  src="{}/src-cpp".format(self.folder_name))
        self.copy("*.a", dst="lib", keep_path=False)
        if tools.os_info.is_macos:
            self.copy("*.dylib*", dst="lib", keep_path=False)
        else:
            self.copy("*.so*", dst="lib", keep_path=False)
        self.copy("LICENSE.*", src=self.folder_name)

    def package_info(self):
        self.cpp_info.libs = ["rdkafka", "rdkafka++"]
