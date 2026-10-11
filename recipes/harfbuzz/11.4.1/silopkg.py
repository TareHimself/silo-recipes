from silo import Component, Package, SiloPackage
from silo.tools.meson import MesonBuild, MesonGenerator
from silo.tools.pkgconfig import PkgConfigDeps


class Harfbuzz(SiloPackage):
    name = "harfbuzz"
    version = "11.4.1"

    def source(self, src):
        src.git(
            "https://github.com/harfbuzz/harfbuzz.git",
            commit="6b285e6e94f0af10c6aa6d31325fd6746aeb2dfe",
        )

    def deps(self):
        self.dep("freetype@2.13.3")
        self.tool("meson@1")
        self.tool("ninja@1.13")
        self.tool("pkgconf@3")

    def generate(self):
        PkgConfigDeps(self).generate()
        meson = MesonGenerator(self)
        meson.set_option("freetype", "enabled")
        for feature in ("glib", "gobject", "cairo", "chafa", "icu", "tests", "docs"):
            meson.set_option(feature, "disabled")
        for feature in ("introspection", "benchmark", "utilities"):
            meson.set_option(feature, "disabled")
        meson.generate()

    def build(self):
        meson = MesonBuild(self)
        meson.configure()
        meson.build()
        meson.install()

    def package(self):
        library = Component(
            "harfbuzz",
            headers=["include/harfbuzz"],
            static_libs=["harfbuzz"],
            requires=["freetype"],
            # C++ inside, and its users are often C programs that would not link this
            system_libs=["stdc++", "m"],
        )
        return Package(components=[library], licenses=["COPYING"])
