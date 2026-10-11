from silo import Component, Package, SiloPackage
from silo.tools.meson import MesonBuild, MesonGenerator
from silo.tools.pkgconfig import PkgConfigDeps


class Pango(SiloPackage):
    name = "pango"
    version = "1.54.0"

    def source(self, src):
        src.git(
            "https://gitlab.gnome.org/GNOME/pango.git",
            commit="5b1551e933d069d15169eb7c8bd6b2e95cbfe230",
        )

    def patch(self, src):
        # Two folders only old, deprecated functions report. Compiled in, they would be
        # paths inside this package.
        build_file = "pango/meson.build"
        src.replace(
            build_file, "'-DSYSCONFDIR=\"@0@\"'.format(pango_sysconfdir)", "'-DSYSCONFDIR=\"/etc\"'"
        )
        src.replace(
            build_file, "'-DLIBDIR=\"@0@\"'.format(pango_libdir)", "'-DLIBDIR=\"/usr/lib\"'"
        )

        # clang 23 counts the unused parent class variable of glib's type macros under this
        src.replace("meson.build", "'-Werror=unused-but-set-variable',", "")

    def deps(self):
        for dependency in (
            "glib@2.78.6",
            "fribidi@1.0.16",
            "harfbuzz@11.4.1",
            "fontconfig@2.15.0",
            "freetype@2.13.3",
            "cairo@1.18.0",
        ):
            self.dep(dependency)
        self.tool("meson@1")
        self.tool("pkgconf@3")

    def generate(self):
        PkgConfigDeps(self).generate()
        meson = MesonGenerator(self)
        for feature in ("cairo", "fontconfig", "freetype"):
            meson.set_option(feature, "enabled")
        for feature in ("introspection", "xft", "libthai", "sysprof"):
            meson.set_option(feature, "disabled")
        meson.set_option("gtk_doc", False)
        meson.set_option("build-testsuite", False)
        meson.set_option("build-examples", False)
        meson.generate()

    def build(self):
        meson = MesonBuild(self)
        meson.configure()
        meson.build()
        meson.install()

    def package(self):
        pango = Component(
            "pango",
            headers=["include/pango-1.0"],
            static_libs=["pango-1.0"],
            requires=["glib", "fribidi", "harfbuzz"],
            system_libs=["m"],
        )
        pangoft2 = Component(
            "pangoft2",
            static_libs=["pangoft2-1.0"],
            requires=["pango::pango", "freetype", "fontconfig"],
        )
        pangocairo = Component(
            "pangocairo",
            static_libs=["pangocairo-1.0"],
            requires=["pango::pango", "pango::pangoft2", "cairo"],
        )
        return Package(components=[pango, pangoft2, pangocairo], licenses=["COPYING"])
