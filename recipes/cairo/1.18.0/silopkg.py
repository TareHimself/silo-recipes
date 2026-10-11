from silo import Component, Package, SiloPackage
from silo.tools.meson import MesonBuild, MesonGenerator
from silo.tools.pkgconfig import PkgConfigDeps

# Names other builds ask pkg-config for, and what each stands for
FEATURES = {
    "cairo-ft": ["freetype"],
    "cairo-fc": ["fontconfig"],
    "cairo-png": ["libpng"],
    "cairo-pdf": ["zlib"],
    "cairo-ps": ["zlib"],
    "cairo-svg": ["libpng"],
}


class Cairo(SiloPackage):
    name = "cairo"
    version = "1.18.0"
    languages = ("c",)

    def source(self, src):
        src.git(
            "https://gitlab.freedesktop.org/cairo/cairo.git",
            commit="3909090108bb2db55330e3eb148aebe664735363",
        )

    def deps(self):
        for dependency in (
            "pixman@0.43.4",
            "freetype@2.13.3",
            "fontconfig@2.15.0",
            "libpng@1.6.59",
            "zlib@1.3.1",
        ):
            self.dep(dependency)
        self.tool("meson@1")
        self.tool("pkgconf@3")

    def generate(self):
        PkgConfigDeps(self).generate()
        meson = MesonGenerator(self)
        for feature in ("fontconfig", "freetype", "png", "zlib"):
            meson.set_option(feature, "enabled")
        for feature in ("glib", "xcb", "xlib", "tests", "spectre", "symbol-lookup"):
            meson.set_option(feature, "disabled")
        meson.generate()

    def build(self):
        meson = MesonBuild(self)
        meson.configure()
        meson.build()
        meson.install()

    def package(self):
        cairo = Component(
            "cairo",
            headers=["include", "include/cairo"],
            static_libs=["cairo"],
            requires=["pixman", "freetype", "fontconfig", "libpng", "zlib"],
            system_libs=["m", "pthread", "dl"],
        )
        features = [
            Component(name, requires=["cairo::cairo", *requires])
            for name, requires in FEATURES.items()
        ]
        return Package(components=[cairo, *features], licenses=["COPYING"])
