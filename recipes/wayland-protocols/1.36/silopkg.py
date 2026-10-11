from silo import Component, Package, SiloPackage
from silo.tools.meson import MesonBuild, MesonGenerator


class WaylandProtocols(SiloPackage):
    name = "wayland-protocols"
    version = "1.36"
    header_only = True

    def source(self, src):
        src.git(
            "https://gitlab.freedesktop.org/wayland/wayland-protocols.git",
            commit="24e612f7d735c014c28e3934440c90c240b3bb9a",
        )

    def deps(self):
        self.tool("meson@1")

    def generate(self):
        meson = MesonGenerator(self)
        meson.set_option("tests", False)
        meson.generate()

    def build(self):
        meson = MesonBuild(self)
        meson.configure()
        meson.build()
        meson.install()

    def package(self):
        # Only protocol descriptions. Builds ask pkg-config where they are.
        protocols = Component(
            "wayland-protocols",
            content=["share/wayland-protocols"],
        )
        return Package(components=[protocols], licenses=["COPYING"])
