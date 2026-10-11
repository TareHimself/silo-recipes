from silo import Component, Package, SiloPackage
from silo.tools.meson import MesonBuild, MesonGenerator


class Libffi(SiloPackage):
    name = "libffi"
    version = "3.4.6"
    languages = ("c",)

    def source(self, src):
        # Upstream builds with autotools. This is the Meson port GStreamer maintains.
        src.git(
            "https://gitlab.freedesktop.org/gstreamer/meson-ports/libffi.git",
            commit="83d0cfd00d7d37af4b4349511d29f1f0512621b3",
        )

    def deps(self):
        self.tool("meson@1")

    def generate(self):
        MesonGenerator(self).generate()

    def build(self):
        meson = MesonBuild(self)
        meson.configure()
        meson.build()
        meson.install()

    def package(self):
        library = Component("libffi", headers=["include"], static_libs=["ffi"])
        return Package(components=[library], licenses=["LICENSE"])
