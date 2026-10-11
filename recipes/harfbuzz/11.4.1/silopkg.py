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

    def patch(self, src):
        # freetype's own pkg-config file counts in library numbers. silo's says the
        # release, so the checks are written in releases (12.0.6 is 2.4.2).
        src.replace(
            "meson.build", "freetype_min_version = '>= 12.0.6'", "freetype_min_version = '>= 2.4.2'"
        )

    def deps(self):
        self.dep("freetype@2.13.3")
        self.tool("meson@1")
        self.tool("pkgconf@3")

    def generate(self):
        PkgConfigDeps(self, aliases={"freetype2": "freetype::freetype"}).generate()
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
