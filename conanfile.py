import os
import shutil
from conans import ConanFile, CMake, tools
from conans.util import files


class LibrdkafkaConan(ConanFile):
    name = "librdkafka"
    sha256 = "2b96d7ed71470b0d0027bd9f0b6eb8fb68ed979f8092611c148771eb01abb72c"

    src_version = "0.11.3"
    version = "0.11.3-dm3"
    license = "BSD 2-Clause"
    url = "https://github.com/ess-dmsc/conan-librdkafka"
    win32_patch_name = "win32.patch"
    win32_sha = "6eeb23b13726d371b737bb39b8d667d36b8793b5"
    description = "The Apache Kafka C/C++ library"
    settings = "os", "compiler", "build_type", "arch"
    build_requires = "cmake_installer/3.10.0@conan/stable"
    options = {"shared": [True, False]}
    default_options = "shared=False"
    exports = "files/*"

    folder_name = "{}-{}".format(name, src_version)
    archive_name = "{}.tar.gz".format(folder_name)

    # For Windows use short paths (ignored for other OS's)
    short_paths=True

    def source(self):
        if tools.os_info.is_windows:
            # For windows we use an RC of 0.11.4 as it has cmake fixes.
            # Once we move to 0.11.4+ this can be removed.
            tools.download(
                "https://github.com/edenhill/librdkafka/archive/{}.tar.gz".format(
                    self.win32_sha
                ),
                self.archive_name
            )
            self.folder_name = "librdkafka-{}".format(self.win32_sha)
        else:
            tools.download(
                "https://github.com/edenhill/librdkafka/archive/v{}.tar.gz".format(
                    self.src_version
                ),
                self.archive_name
            )
            tools.check_sha256(
                self.archive_name,
                self.sha256
            )
        tools.unzip(self.archive_name)
        os.unlink(self.archive_name)

    def build(self):
        if tools.os_info.is_windows:
            # Can be removed after moving to 0.11.4
            self.folder_name = "librdkafka-{}".format(self.win32_sha)
            patch = os.path.join(self.source_folder, "files", self.win32_patch_name)
            tools.patch(base_path=self.folder_name, patch_file=patch)
        
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

            if tools.os_info.is_windows:
                # Enables overridding of default window build settings
                cmake.definitions["WITHOUT_WIN32_CONFIG"] = "ON"

            cmake.configure(source_dir="..", build_dir=".")
            cmake.build(build_dir=".")

            os.rename("../LICENSE", "../LICENSE.librdkafka")

    def package(self):
        self.copy("rdkafka.h", dst="include/librdkafka",
                  src="{}/src".format(self.folder_name))
        self.copy("rdkafkacpp.h", dst="include/librdkafka",
                  src="{}/src-cpp".format(self.folder_name))

        if tools.os_info.is_windows:
            self.copy("*.dll", dst="bin", keep_path=False)
        else:
            self.copy("*.a", dst="lib", keep_path=False)

        if tools.os_info.is_macos:
            self.copy("*.dylib*", dst="lib", keep_path=False)
        elif tools.os_info.is_windows:
            self.copy("*.lib", dst="lib", keep_path=False)
        else:
            self.copy("*.so*", dst="lib", keep_path=False)
        self.copy("LICENSE.*", src=self.folder_name)

    def package_info(self):
        self.cpp_info.libs = ["rdkafka", "rdkafka++"]
