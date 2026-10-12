from silo import Component, Package, SiloPackage
from silo.tools.meson import MesonBuild, MesonGenerator


class ProxyLibintl(SiloPackage):
    """The gettext functions for a system whose C library has none: Windows, macOS, musl.

    They hand every message back untranslated, which is all a library such as glib needs
    to build and run.
    """

    name = "proxy-libintl"
    version = "0.4"
    languages = ("c",)

    def source(self, src):
        src.git(
            "https://github.com/frida/proxy-libintl.git",
            commit="c03e1a74b17fa7ec467e110130775409e4828a4c",
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
        library = Component(
            "intl",
            headers=["include"],
            static_libs=["intl"],
            defines=["G_INTL_STATIC_COMPILATION"],
        )
        return Package(components=[library], licenses=["COPYING"])
