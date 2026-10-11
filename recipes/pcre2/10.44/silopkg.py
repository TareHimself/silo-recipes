from silo import Component, Package, SiloPackage
from silo.tools.cmake import CMakeBuild, CMakeGenerator


class Pcre2(SiloPackage):
    name = "pcre2"
    version = "10.44"
    languages = ("c",)

    def source(self, src):
        src.git(
            "https://github.com/PCRE2Project/pcre2.git",
            commit="6ae58beca071f13ccfed31d03b3f479ab520639b",
        )

    def deps(self):
        self.tool("cmake@4.3")
        self.tool("ninja@1.13")

    def generate(self):
        toolchain = CMakeGenerator(self)
        toolchain.add_cache_bool("BUILD_SHARED_LIBS", False)
        toolchain.add_cache_bool("PCRE2_BUILD_PCRE2GREP", False)
        toolchain.add_cache_bool("PCRE2_BUILD_TESTS", False)
        toolchain.add_cache_bool("PCRE2_STATIC_RUNTIME", False)
        toolchain.generate()

    def build(self):
        cmake = CMakeBuild(self)
        cmake.configure()
        cmake.build()
        cmake.install()

    def package(self):
        library = Component(
            "pcre2-8",
            headers=["include"],
            static_libs=["pcre2-8"],
            defines=["PCRE2_STATIC"],
            pkg_config="libpcre2-8",
        )
        return Package(components=[library], licenses=["LICENCE"])
