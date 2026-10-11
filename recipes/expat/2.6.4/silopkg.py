from silo import Component, Package, SiloPackage
from silo.enums import Platform
from silo.tools.cmake import CMakeBuild, CMakeGenerator


class Expat(SiloPackage):
    name = "expat"
    version = "2.6.4"
    languages = ("c",)

    def source(self, src):
        src.fetch(
            "https://github.com/libexpat/libexpat/releases/download/R_2_6_4/expat-2.6.4.tar.xz",
            sha256="a695629dae047055b37d50a0ff4776d1d45d0a4c842cf4ccee158441f55ff7ee",
        )

    def deps(self):
        self.tool("cmake@4.3")

    def generate(self):
        toolchain = CMakeGenerator(self)
        toolchain.add_cache_bool("EXPAT_SHARED_LIBS", False)
        toolchain.add_cache_bool("EXPAT_BUILD_TOOLS", False)
        toolchain.add_cache_bool("EXPAT_BUILD_EXAMPLES", False)
        toolchain.add_cache_bool("EXPAT_BUILD_TESTS", False)
        toolchain.add_cache_bool("EXPAT_BUILD_DOCS", False)
        toolchain.add_cache_bool("EXPAT_MSVC_STATIC_CRT", False)
        toolchain.generate()

    def build(self):
        cmake = CMakeBuild(self)
        cmake.configure()
        cmake.build()
        cmake.install()

    def package(self):
        windows = self.profile.settings.os is Platform.Windows
        library = Component(
            "expat",
            headers=["include"],
            static_libs=["libexpatMD" if windows else "expat"],
            defines=["XML_STATIC"],
        )
        return Package(components=[library], licenses=["COPYING"])
