from silo import Component, Package, SiloPackage
from silo.enums import Platform
from silo.tools.cmake import CMakeBuild, CMakeDeps, CMakeGenerator


class Vorbis(SiloPackage):
    name = "vorbis"
    version = "1.3.7"
    languages = ("c",)

    def source(self, src):
        src.fetch(
            "https://downloads.xiph.org/releases/vorbis/libvorbis-1.3.7.tar.xz",
            sha256="b33cc4934322bcbf6efcbacf49e3ca01aadbea4114ec9589d1b1e9d20f72954b",
        )

    def deps(self):
        self.dep("ogg@1.3.5")
        self.tool("cmake@4.3")

    def generate(self):
        deps = CMakeDeps(self)
        deps.alias("Ogg::ogg", "ogg::ogg")
        deps.generate()
        toolchain = CMakeGenerator(self)
        toolchain.add_cache_string("CMAKE_POLICY_VERSION_MINIMUM", "3.5")
        toolchain.add_cache_bool("BUILD_SHARED_LIBS", False)
        toolchain.add_cache_bool("INSTALL_CMAKE_PACKAGE_MODULE", False)
        toolchain.generate()

    def build(self):
        cmake = CMakeBuild(self)
        cmake.configure()
        cmake.build()
        cmake.install()

    def package(self):
        system_libs = ["m"] if self.profile.settings.os is Platform.Linux else []
        return Package(
            components=[
                Component(
                    "vorbis",
                    headers=["include"],
                    static_libs=["vorbis"],
                    requires=["ogg::ogg"],
                    system_libs=system_libs,
                ),
                Component("vorbisenc", static_libs=["vorbisenc"], requires=["vorbis::vorbis"]),
                Component("vorbisfile", static_libs=["vorbisfile"], requires=["vorbis::vorbis"]),
            ],
            licenses=["COPYING"],
        )
