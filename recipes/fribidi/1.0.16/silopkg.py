from silo import Component, Package, SiloPackage
from silo.tools.meson import MesonBuild, MesonGenerator


class Fribidi(SiloPackage):
    name = "fribidi"
    version = "1.0.16"
    languages = ("c",)

    def source(self, src):
        src.git(
            "https://github.com/fribidi/fribidi.git",
            commit="68162babff4f39c4e2dc164a5e825af93bda9983",
        )

    def deps(self):
        self.tool("meson@1")
        self.tool("ninja@1.13")

    def generate(self):
        meson = MesonGenerator(self)
        meson.set_option("docs", False)
        meson.set_option("tests", False)
        meson.set_option("bin", False)
        meson.generate()

    def build(self):
        meson = MesonBuild(self)
        meson.configure()
        meson.build()
        meson.install()

    def package(self):
        library = Component(
            "fribidi",
            headers=["include/fribidi"],
            static_libs=["fribidi"],
            defines=["FRIBIDI_LIB_STATIC"],
        )
        return Package(components=[library], licenses=["COPYING"])
