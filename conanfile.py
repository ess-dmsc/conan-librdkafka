import os
from conans import ConanFile, tools


class LibrdkafkaConan(ConanFile):
    name = "librdkafka"
    version = "0.11.0"
    license = "BSD 2-Clause"
    url = "https://github.com/ess-dmsc/conan-librdkafka"
    settings = "os", "compiler", "build_type", "arch"

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
        with tools.chdir("./librdkafka-0.11.0"):
            # Do not link using absolute rpath in macOS.
            tools.replace_in_file(
                "mklove/modules/configure.lib",
                " -Wl,-install_name,$(DESTDIR)$(libdir)/$(LIBFILENAME)",
                ""
            )
            self.run(
                "./configure"
                " --prefix="
                " --disable-lz4"
                " --disable-ssl"
                " --disable-sasl"
            )
            self.run("make")

    def package(self):
        self.copy("rdkafka.h", dst="include/librdkafka",
                  src="librdkafka-0.11.0/src")
        self.copy("rdkafkacpp.h", dst="include/librdkafka",
                  src="librdkafka-0.11.0/src-cpp")
        self.copy("*.so*", dst="lib", keep_path=False)
        self.copy("*.a", dst="lib", keep_path=False)
        self.copy("*.pc", dst="lib/pkgconfig", keep_path=False)
        if tools.os_info.is_macos:
            self.copy("*.dylib*", dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ["rdkafka", "rdkafka++"]
