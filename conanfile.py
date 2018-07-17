import os
from conans import ConanFile, CMake, AutoToolsBuildEnvironment, tools
from conans.util import files


class LibrdkafkaConan(ConanFile):
    name = "librdkafka"
    sha256 = "9d8f1eb7b0e29e9ab1168347c939cb7ae5dff00a39cef99e7ef033fd8f92737c"

    src_version = "0.11.4"
    version = src_version
    license = "BSD 2-Clause"
    url = "https://github.com/ess-dmsc/conan-librdkafka"
    description = "The Apache Kafka C/C++ library"
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"
    build_requires = "cmake_installer/3.10.0@conan/stable"

    options = { "shared": [True, False],
                "fPIC": [True, False],
                "build_examples": [False, True],
                "build_tests": [False, True],
                "with_zlib": [True, False],
                "with_openssl": [True, False],
                "with_devel_asserts" : [True, False],
                "with_refcount_debug" : [True, False],
                "with_sharedptr_debug": [True, False],
                "with_optimization": [True, False] }

    default_options = ( "shared=False", "fPIC=False", "build_examples=False", "build_tests=False", 
                        "with_zlib=False", "with_openssl=False", "with_devel_asserts=False", 
                        "with_refcount_debug=False", "with_sharedptr_debug=False", "with_optimization=False" )

    folder_name = "{}-{}".format(name, src_version)
    archive_name = "{}.tar.gz".format(folder_name)
    
    # For Windows use short paths (ignored for other OS's)
    short_paths=True

    def requirements(self):
        if self.options.with_zlib:
            self.requires('zlib/1.2.11@conan/stable', private=True)
        if self.options.with_openssl:
            self.requires('OpenSSL/1.0.2o@conan/stable')

    def configure(self):
        # Remove these options on Windows because they require
        # UNIX/BSD-specific header files and functions
        if self.settings.os == 'Windows':
            if self.options.build_tests:
                self.output.warn('Ignoring build_tests option on Windows')
                self.options.build_tests = False

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

    def build(self):
    
        self.output.info("cwd=%s" % (os.getcwd()))

        # put conan inclusion into CMakeLists.txt file or fail (strict=True)
        self.output.info('Patching CMakeLists.txt')
        tools.replace_in_file(os.sep.join([self.folder_name, "CMakeLists.txt"]), "project(RdKafka)",
        '''project(RdKafka)
           include(${CMAKE_BINARY_DIR}/../../conanbuildinfo.cmake)
           conan_basic_setup()''')

        # Respect Conan's shared/fPIC options
        self.output.info('Patching src/CMakeLists.txt')
        tools.replace_in_file(
            os.sep.join([self.folder_name, "src", "CMakeLists.txt"]),
            "add_library(rdkafka SHARED ${sources})",
            '''add_definitions(-D{})
            add_library(rdkafka ${{sources}})'''.format(
                'LIBRDKAFKA_EXPORTS' if self.options.shared else
                'LIBRDKAFKA_STATICLIB'))

        # Some situations like using a bad passphrase causes rk to never be initialized
        # so calling this function would cause a segfault.  Input validation would be helpful.
        tools.replace_in_file(os.sep.join([self.folder_name, "src", "rdkafka.c"]), 
        '''static void rd_kafka_destroy_app (rd_kafka_t *rk, int blocking) {
        thrd_t thrd;
#ifndef _MSC_VER
	int term_sig = rk->rk_conf.term_sig;
#endif''',
'''static void rd_kafka_destroy_app (rd_kafka_t *rk, int blocking) {
        if (rk == NULL)
        {
            return;
        }
        thrd_t thrd;
#ifndef _MSC_VER
	int term_sig = rk->rk_conf.term_sig;
#endif''')
        
        if tools.os_info.is_windows:
                
            # rdkafka C++ library does not export the special partition and offset constants/values 
            # variables from the DLL, and looks like the library is switching to a preprocessor define 
            # instead.  This change includes the C-header file just to get the macro values, and then 
            # changes the constants from being used as imported values to read from the macros.
            tools.replace_in_file(os.sep.join([self.folder_name, "examples", "rdkafka_example.cpp"]), '#include "rdkafkacpp.h"', 
    '''#include "rdkafkacpp.h"
    #include "rdkafka.h"''')
            tools.replace_in_file(os.sep.join([self.folder_name, "examples", "rdkafka_example.cpp"]), 'RdKafka::Topic::PARTITION_UA', 'RD_KAFKA_PARTITION_UA')
            tools.replace_in_file(os.sep.join([self.folder_name, "examples", "rdkafka_example.cpp"]), 'RdKafka::Topic::OFFSET_BEGINNING', 'RD_KAFKA_OFFSET_BEGINNING')
            tools.replace_in_file(os.sep.join([self.folder_name, "examples", "rdkafka_example.cpp"]), 'RdKafka::Topic::OFFSET_END', 'RD_KAFKA_OFFSET_END')
            tools.replace_in_file(os.sep.join([self.folder_name, "examples", "rdkafka_example.cpp"]), 'RdKafka::Topic::OFFSET_STORED', 'RD_KAFKA_OFFSET_STORED')
        

            # src/rd.h includes win32_config.h which is not generated by CMake/Conan 
            # so it builds librdkafka with fixed settings (!!!).
            # This change removes that choice, and  both platforms use the generated config.h file
            self.output.info('Patching src/rd.h file')
            tools.replace_in_file(os.sep.join([self.folder_name, 'src', 'rd.h']),
'''
#ifdef _MSC_VER
/* Visual Studio */
#include "win32_config.h"
#else
/* POSIX / UNIX based systems */
#include "../config.h" /* mklove output */
#endif
''',
'#include "../config.h"')

            # librdkafka inconsistently defines its exports definition, so this defines it according to rdkafkacpp.h
            self.output.info('Patching src-cpp/CMakeLists.txt file')
            tools.replace_in_file(os.sep.join([self.folder_name, 'src-cpp', 'CMakeLists.txt']),
                'add_library(',
                '''
                add_definitions(-D{})
                add_library(
                '''.format('LIBRDKAFKACPP_EXPORTS' if self.options.shared else
                           'LIBRDKAFKA_STATICLIB')
            )

            files.mkdir("./{}/build".format(self.folder_name))
            with tools.chdir("./{}/build".format(self.folder_name)):
                cmake = CMake(self)

                cmake.definitions['RDKAFKA_BUILD_STATIC'] = "OFF" if self.options.shared else "ON"
                
                cmake.definitions['ENABLE_DEVEL'] = "ON" if self.options.with_devel_asserts else "OFF"
                cmake.definitions['ENABLE_REFCNT_DEBUG'] = 'ON' if self.options.with_refcount_debug else "OFF"
                cmake.definitions['ENABLE_SHAREDPTR_DEBUG'] = 'ON' if self.options.with_sharedptr_debug else "OFF"
                
                cmake.definitions["RDKAFKA_BUILD_EXAMPLES"] = "ON" if self.options.build_examples else "OFF"
                cmake.definitions["RDKAFKA_BUILD_TESTS"] = "ON"  if self.options.build_tests else "OFF"
                cmake.definitions["WITH_LIBDL"] = "OFF"
                cmake.definitions["WITH_PLUGINS"] = "OFF"
                cmake.definitions["WITH_SASL"] = "OFF"
                cmake.definitions["WITH_SSL"] = "ON" if self.options.with_openssl else "OFF"
                cmake.definitions["WITH_ZLIB"] = "ON" if self.options.with_zlib else "OFF"

                if self.settings.build_type == "Debug":
                    cmake.definitions["WITHOUT_OPTIMIZATION"] = "ON"
                if self.options.shared:
                    cmake.definitions["BUILD_SHARED_LIBS"] = "ON"

                # Enables overridding of default window build settings
                cmake.definitions["WITHOUT_WIN32_CONFIG"] = "ON"

                cmake.configure(source_dir="..", build_dir=".")
                cmake.build(build_dir=".")
        else:
            configure_args = [
                "--prefix=",
                "--disable-sasl"
            ]

            if not self.options.with_openssl:
                configure_args.append('--disable-ssl')
            if not self.options.with_zlib:
                configure_args.append('--disable-lz4')

            if self.options.shared:
                ldflags = os.environ.get("LDFLAGS", "")
                if tools.os_info.is_linux:
                    os.environ["LDFLAGS"] = ldflags + " -Wl,-rpath=\\$$ORIGIN"
                elif tools.os_info.is_macos:
                    os.environ["LDFLAGS"] = ldflags + " -headerpad_max_install_names"
            else:
                configure_args.append("--enable-static")

            if self.settings.build_type == "Debug":
                configure_args.append("--disable-optimization")

            destdir = os.path.join(os.getcwd(), "install")
            with tools.chdir(self.folder_name):
                if tools.os_info.is_macos and self.options.shared:
                    path = os.path.join(os.getcwd(), "mklove", "modules", "configure.lib")
                    tools.replace_in_file(
                        path,
                         '-dynamiclib -Wl,-install_name,$(DESTDIR)$(libdir)/$(LIBFILENAME)',
                         '-dynamiclib -Wl,-install_name,@rpath/$(LIBFILENAME)',
                    )

                env_build = AutoToolsBuildEnvironment(self)
                env_build.configure(args=configure_args)
                env_build.make()
                env_build.make(args=["install", "DESTDIR="+destdir])

        with tools.chdir(self.folder_name):
            os.rename("LICENSE", "LICENSE.librdkafka")

    def package(self):
        if tools.os_info.is_windows:
            self.copy("rdkafka.h", dst="include/librdkafka",
                      src="{}/src".format(self.folder_name))
            self.copy("rdkafkacpp.h", dst="include/librdkafka",
                      src="{}/src-cpp".format(self.folder_name))
        
            # Copy Windows import libraries, program DB's, export, linker input files, etc...
            self.copy("*.lib", src=os.sep.join([self.folder_name, 'build', 'lib' ]), dst="lib", keep_path=False, excludes="configure.lib")
            self.copy("*.exp", src=os.sep.join([self.folder_name, 'build', 'lib' ]), dst="lib", keep_path=False)
            self.copy("*.pdb", src=os.sep.join([self.folder_name, 'build', 'lib' ]), dst="bin", keep_path=False)
            
            self.copy("*.dll", src=os.sep.join([self.folder_name, 'build', 'bin' ]), dst="bin", keep_path=False)
            self.copy("*.ilk", src=os.sep.join([self.folder_name, 'build', 'lib' ]), dst="bin", keep_path=False)
            self.copy("*.pdb", src=os.sep.join([self.folder_name, 'build', 'bin' ]), dst="bin", keep_path=False)

            # copy example executables (if they exist) with somewhat restrictive patterns
            for example_bin in ['kafkatest_verifiable_client*', 'rdkafka_consumer_example*', \
                                'rdkafka_example*', 'rdkafka_performance*', 'rdkafka_simple_producer*', \
                                'rdkafka_test*']:

                self.copy(example_bin, src=os.sep.join([self.folder_name, 'build', 'bin' ]), dst="bin", keep_path=False)

            # Copy Linux/Mac files
            self.copy("*.a", dst="lib", keep_path=False)
            self.copy("*.lib", dst="lib", keep_path=False, excludes="configure.lib")
            self.copy("LICENSE.*", src=self.folder_name)
        else:
            install_folder = os.path.join(self.build_folder, "install")
            self.copy("*.h", src=install_folder)
            if self.options.shared:
                if tools.os_info.is_linux:
                    self.copy("*.so*", src=install_folder, symlinks=True)
                elif tools.os_info.is_macos:
                    self.copy("*.dylib*", src=install_folder)
            else:
                self.copy("*.a", src=install_folder)
            self.copy("LICENSE.*", src=self.folder_name)

    def package_info(self):
        self.cpp_info.libs = ["rdkafka++", "rdkafka"]
        if self.settings.os == 'Linux':
            self.cpp_info.libs.extend([ 'rt', 'dl' ])
        if not self.options.shared:
            self.cpp_info.defines.append('LIBRDKAFKA_STATICLIB')
