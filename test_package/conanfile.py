from conans import ConanFile, CMake, tools, RunEnvironment
import os


class LibrdkafkaTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    def build(self):
        cmake = CMake(self)

        # Current dir is "test_package/build/<build_id>" and CMakeLists.txt is
        # in "test_package".
        cmake.configure(source_dir=self.source_folder, build_dir="./")
        cmake.build()

    def imports(self):
        self.copy("*.dll", dst="bin", src="lib")
        self.copy("*.dylib*", dst="bin", src="lib")
        self.copy("*.so*", dst="bin", src="lib")

    def test(self):
        os.chdir("bin")
        env_build = RunEnvironment(self)
        with tools.environment_append(env_build.vars):
            self.run(".%sexample" % os.sep)
