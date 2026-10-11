from silo import Component, Package, SiloPackage
from silo.tools.meson import MesonBuild, MesonGenerator
from silo.tools.pkgconfig import PkgConfigDeps


class Xkbcommon(SiloPackage):
    """Keyboard layouts and key symbols. The layout data is the machine's, from xkeyboard-config."""

    name = "xkbcommon"
    version = "1.6.0"
    languages = ("c",)

    def source(self, src):
        src.git(
            "https://github.com/xkbcommon/libxkbcommon.git",
            commit="d2a08f761c796733e42fac4099f5c38d443e88e1",
        )

    def deps(self):
        self.tool("bison@3.8.2")
        self.tool("meson@1")
        self.tool("ninja@1.13")
        self.tool("pkgconf@3")

    def generate(self):
        PkgConfigDeps(self).generate()
        meson = MesonGenerator(self)
        meson.set_builtin("default_library", "static")
        for feature in ("x11", "wayland", "xkbregistry", "docs", "tools", "bash-completion"):
            meson.set_option(f"enable-{feature}", False)
        meson.set_builtin("sysconfdir", "/etc")
        meson.set_option("xkb-config-root", "/usr/share/X11/xkb")
        meson.set_option("x-locale-root", "/usr/share/X11/locale")
        meson.generate()

    def build(self):
        meson = MesonBuild(self)
        meson.configure()
        meson.build()
        meson.install()

    def package(self):
        library = Component(
            "xkbcommon",
            headers=["include"],
            static_libs=["xkbcommon"],
            pkg_config="xkbcommon",
        )
        return Package(components=[library], licenses=["LICENSE"])
