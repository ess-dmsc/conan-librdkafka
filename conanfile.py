import os
from conans import ConanFile, CMake, tools
from conans.util import files


class LibrdkafkaConan(ConanFile):
    name = "librdkafka"
    sha256 = "2b96d7ed71470b0d0027bd9f0b6eb8fb68ed979f8092611c148771eb01abb72c"

    src_version = "0.11.3"
    version = "0.11.3-dm2"
    license = "BSD 2-Clause"
    url = "https://github.com/ess-dmsc/conan-librdkafka"
    description = "The Apache Kafka C/C++ library"
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"
    build_requires = "cmake_installer/3.10.0@conan/stable"
    options = { "shared": [True, False],
                "build_examples": [False, True],
                "build_tests": [False, True],
                "with_zlib": [True, False],
                "with_openssl": [True, False] }
    default_options = "shared=False", "build_examples=False", "build_tests=False", "with_zlib=False", "with_openssl=False"

    folder_name = "{}-{}".format(name, src_version)
    archive_name = "{}.tar.gz".format(folder_name)

    def requirements(self):
        if self.options.with_zlib:
            self.requires('zlib/1.2.11@conan/stable', private=True)
        if self.options.with_openssl:
            self.requires('OpenSSL/1.1.0g@conan/stable')

    def source(self):
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

        # put conan inclusion into CMakeLists.txt file or fail (strict=True)
        tools.replace_in_file(os.sep.join([self.folder_name, "CMakeLists.txt"]), "project(RdKafka)",
        '''project(RdKafka)
           include(${CMAKE_BINARY_DIR}/../../conanbuildinfo.cmake)
           conan_basic_setup()''')

        if self.options.build_tests:
            self.output.info('Patching tests/CMakeLists.txt file')
            tools.replace_in_file(os.sep.join([self.folder_name, "tests", "CMakeLists.txt"]), 
                "target_link_libraries(rdkafka_test PUBLIC rdkafka++)",
                '''
if(MSVC)
target_link_libraries(rdkafka_test PUBLIC rdkafka++)
elseif(UNIX)
# Also link to librt (clock_gettime) and libdl (for dlopen, etc...)
target_link_libraries(rdkafka_test PUBLIC rdkafka++ rt dl)
endif(MSVC)''')

        if self.options.build_examples:
            # Replace target_link_library lines that link to the C library specifically (rdkafka)
            for exe_name in [ 'rdkafka_simple_producer', 'rdkafka_consumer_example', 'rdkafka_performance', 'rdkafka_example' ]:
                self.output.info('Patching executable %s in examples/CMakeLists.txt file' % (exe_name))

                tools.replace_in_file(os.sep.join([self.folder_name, "examples", "CMakeLists.txt"]), 
                "target_link_libraries(%s PUBLIC rdkafka)" % (exe_name),
                '''
if(MSVC)
target_link_libraries(%s PUBLIC rdkafka)
elseif(UNIX)
# Also link to librt (clock_gettime) and libdl (for dlopen, etc...)
target_link_libraries(%s PUBLIC rdkafka rt dl)
endif(MSVC)''' % (exe_name, exe_name))

            # Replace target_link_library lines that link to the C++ library specifically (rdkafka++)
            for exe_name in ['rdkafka_example_cpp', 'rdkafka_consumer_example_cpp', 'kafkatest_verifiable_client' ]:
                self.output.info('Patching executable %s in examples/CMakeLists.txt file' % (exe_name))

                tools.replace_in_file(os.sep.join([self.folder_name, "examples", "CMakeLists.txt"]), 
                "target_link_libraries(%s PUBLIC rdkafka++)" % (exe_name),
                '''
if(MSVC)
target_link_libraries(%s PUBLIC rdkafka++)
elseif(UNIX)
# Also link to librt (clock_gettime) and libdl (for dlopen, etc...)
target_link_libraries(%s PUBLIC rdkafka++ rt dl)
endif(MSVC)''' % (exe_name, exe_name))


    def build(self):
        files.mkdir("./{}/build".format(self.folder_name))
        with tools.chdir("./{}/build".format(self.folder_name)):
            cmake = CMake(self)

            cmake.definitions["RDKAFKA_BUILD_EXAMPLES"] = "ON" if self.options.build_examples else "OFF"
            cmake.definitions["RDKAFKA_BUILD_TESTS"] = "ON"  if self.options.build_tests else "OFF"
            cmake.definitions["WITH_LIBDL"] = "OFF"
            cmake.definitions["WITH_PLUGINS"] = "OFF"
            cmake.definitions["WITH_SASL"] = "OFF"
            cmake.definitions["WITH_SSL"] = "ON" if self.options.with_openssl else "OFF"
            cmake.definitions["WITH_ZLIB"] = "ON" if self.options.with_zlib else "OFF"
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
            self.copy("*.so*", dst="lib", keep_path=False, symlinks=True)
        self.copy("LICENSE.*", src=self.folder_name)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == 'Linux':
            self.cpp_info.libs.extend([ 'rt', 'dl' ])
        
