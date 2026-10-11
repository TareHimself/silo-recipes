from silo import Component, Package, SiloPackage
from silo.tools.cmake import CMakeBuild, CMakeGenerator


class Ogg(SiloPackage):
    name = "ogg"
    version = "1.3.5"
    languages = ("c",)

    def source(self, src):
        src.fetch(
            "https://downloads.xiph.org/releases/ogg/libogg-1.3.5.tar.xz",
            sha256="c4d91be36fc8e54deae7575241e03f4211eb102afb3fc0775fbbc1b740016705",
        )

    def deps(self):
        self.tool("cmake@4.3")

    def generate(self):
        toolchain = CMakeGenerator(self)
        toolchain.add_cache_string("CMAKE_POLICY_VERSION_MINIMUM", "3.5")
        toolchain.add_cache_bool("BUILD_SHARED_LIBS", False)
        toolchain.add_cache_bool("BUILD_TESTING", False)
        toolchain.add_cache_bool("INSTALL_DOCS", False)
        toolchain.add_cache_bool("INSTALL_PKG_CONFIG_MODULE", False)
        toolchain.add_cache_bool("INSTALL_CMAKE_PACKAGE_MODULE", False)
        toolchain.generate()

    def build(self):
        cmake = CMakeBuild(self)
        cmake.configure()
        cmake.build()
        cmake.install()

    def package(self):
        return Package(
            components=[Component("ogg", headers=["include"], static_libs=["ogg"])],
            licenses=["COPYING"],
        )
