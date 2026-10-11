from silo import Component, Package, SiloPackage
from silo.tools.meson import MesonBuild, MesonGenerator
from silo.tools.pkgconfig import PkgConfigDeps

PLUGINS = "lib/libdecor/plugins-1"


class Libdecor(SiloPackage):
    """Window decorations for Wayland programs. Upstream only builds it shared."""

    name = "libdecor"
    version = "0.2.2"
    languages = ("c",)

    def source(self, src):
        src.git(
            "https://gitlab.freedesktop.org/libdecor/libdecor.git",
            commit="7807ae3480f5c6a37c5e8505d94af1e764aaf704",
        )

    def patch(self, src):
        # Upstream compiles its plugin folder in, which would be a path inside this
        # package. A program sets LIBDECOR_PLUGIN_DIR to the folder this package holds.
        src.replace(
            "meson.build",
            "cdata.set_quoted('LIBDECOR_PLUGIN_DIR', plugindir)",
            "cdata.set_quoted('LIBDECOR_PLUGIN_DIR', '/var/empty/libdecor-plugins')",
        )

    def deps(self):
        for dependency in (
            "wayland@1.22.0",
            "wayland-protocols@1.36",
            "cairo@1.18.0",
            "pango@1.54.0",
        ):
            self.dep(dependency)
        # For wayland-scanner, which turns protocol descriptions into code
        self.tool("wayland@1.22.0")
        self.tool("meson@1")
        self.tool("pkgconf@3")

    def generate(self):
        PkgConfigDeps(self).generate()
        meson = MesonGenerator(self)
        meson.set_builtin("default_library", "shared")
        meson.set_option("demo", False)
        meson.set_option("install_demo", False)
        meson.set_option("gtk", "disabled")
        meson.set_option("dbus", "disabled")
        meson.generate()

    def build(self):
        meson = MesonBuild(self)
        meson.configure()
        meson.build()
        meson.install()

    def package(self):
        library = Component(
            "libdecor",
            headers=["include/libdecor-0"],
            shared_libs=["decor-0"],
            content=[PLUGINS],
            requires=["wayland::wayland-client"],
            system_libs=["m"],
        )
        return Package(components=[library], licenses=["LICENSE"])
