from silo import Component, Package, SiloPackage
from silo.enums import Platform
from silo.tools.cmake import CMakeBuild, CMakeDeps, CMakeGenerator


class Libpng(SiloPackage):
    name = "libpng"
    version = "1.6.59"
    languages = ("c",)

    def source(self, src):
        src.git(
            "https://github.com/pnggroup/libpng.git",
            commit="cd952f49f95bb27154ae77dbb103032d95f6e580",
        )

    def deps(self):
        self.dep("zlib@1.3.1")
        self.tool("cmake@4.3")

    def generate(self):
        deps = CMakeDeps(self)
        deps.alias("ZLIB::ZLIB", "zlib::zlib")
        deps.generate()
        toolchain = CMakeGenerator(self)
        toolchain.add_cache_bool("PNG_SHARED", False)
        toolchain.add_cache_bool("PNG_TESTS", False)
        toolchain.add_cache_bool("PNG_TOOLS", False)
        toolchain.generate()

    def build(self):
        cmake = CMakeBuild(self)
        cmake.configure()
        cmake.build()
        cmake.install()

    def package(self):
        windows = self.profile.settings.os is Platform.Windows
        return Package(
            components=[
                Component(
                    "libpng",
                    headers=["include"],
                    static_libs=["libpng16_static" if windows else "png16"],
                    requires=["zlib"],
                )
            ],
            licenses=["LICENSE"],
        )
