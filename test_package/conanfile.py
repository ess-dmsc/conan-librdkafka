from conans import ConanFile, CMake, tools, RunEnvironment
import os


class LibrdkafkaTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def imports(self):
        self.copy("*.dylib*", dst="bin", src="lib")
        self.copy("*.so*", dst="bin", src="lib")

    def test(self):
        os.chdir("bin")
        env_build = RunEnvironment(self)
        with tools.environment_append(env_build.vars):
            self.run(".%sexample" % os.sep)
