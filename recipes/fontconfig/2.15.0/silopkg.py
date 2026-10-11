from silo import Component, Package, SiloPackage
from silo.tools.meson import MesonBuild, MesonGenerator
from silo.tools.pkgconfig import PkgConfigDeps


class Fontconfig(SiloPackage):
    name = "fontconfig"
    version = "2.15.0"
    languages = ("c",)

    def source(self, src):
        src.fetch(
            "https://www.freedesktop.org/software/fontconfig/release/fontconfig-2.15.0.tar.xz",
            sha256="63a0658d0e06e0fa886106452b58ef04f21f58202ea02a94c39de0d3335d7c0e",
        )

    def patch(self, src):
        # freetype's own pkg-config file counts in library numbers. silo's says the
        # release, so the checks are written in releases (21.0.15 is 2.8.1).
        src.replace("meson.build", "freetype_req = '>= 21.0.15'", "freetype_req = '>= 2.8.1'")

    def deps(self):
        self.dep("freetype@2.13.3")
        self.dep("expat@2.6.4")
        self.tool("gperf@3.1")
        self.tool("meson@1")
        self.tool("pkgconf@3")

    def generate(self):
        PkgConfigDeps(self, aliases={"freetype2": "freetype::freetype"}).generate()
        meson = MesonGenerator(self)
        # Fonts and their configuration belong to the machine, not to this package
        meson.set_builtin("sysconfdir", "/etc")
        meson.set_builtin("localstatedir", "/var")
        meson.set_option("template-dir", "/usr/share/fontconfig/conf.avail")
        meson.set_option("xml-dir", "/usr/share/xml/fontconfig")
        for feature in ("doc", "tests", "tools", "nls", "cache-build"):
            meson.set_option(feature, "disabled")
        meson.generate()

    def build(self):
        meson = MesonBuild(self)
        meson.configure()
        meson.build()
        meson.install()

    def package(self):
        library = Component(
            "fontconfig",
            headers=["include"],
            static_libs=["fontconfig"],
            requires=["freetype", "expat"],
            system_libs=["m", "pthread"],
        )
        return Package(components=[library], licenses=["COPYING"])
