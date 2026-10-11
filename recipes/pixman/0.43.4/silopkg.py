from silo import Component, Package, SiloPackage
from silo.tools.meson import MesonBuild, MesonGenerator


class Pixman(SiloPackage):
    name = "pixman"
    version = "0.43.4"
    languages = ("c",)

    def source(self, src):
        src.git(
            "https://gitlab.freedesktop.org/pixman/pixman.git",
            commit="54cad71674ec485cbbbf49876feaa8a69b97c828",
        )

    def deps(self):
        self.tool("meson@1")

    def generate(self):
        meson = MesonGenerator(self)
        for feature in ("tests", "demos", "gtk", "libpng", "openmp"):
            meson.set_option(feature, "disabled")
        meson.generate()

    def build(self):
        meson = MesonBuild(self)
        meson.configure()
        meson.build()
        meson.install()

    def package(self):
        library = Component(
            "pixman-1",
            headers=["include/pixman-1"],
            static_libs=["pixman-1"],
            system_libs=["m", "pthread"],
        )
        return Package(components=[library], licenses=["COPYING"])
