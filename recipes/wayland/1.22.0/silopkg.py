from silo import Component, Options, Package, SiloPackage
from silo.tools.meson import MesonBuild, MesonGenerator
from silo.tools.pkgconfig import PkgConfigDeps


class WaylandOptions(Options):
    # Two static copies in one program define the same symbols twice
    shared: bool = True


class Wayland(SiloPackage[WaylandOptions]):
    name = "wayland"
    version = "1.22.0"
    languages = ("c",)
    supports_shared = True

    def source(self, src):
        src.git(
            "https://gitlab.freedesktop.org/wayland/wayland.git",
            commit="b2649cb3ee6bd70828a17e50beb16591e6066288",
        )

    def deps(self):
        self.dep("libffi@3.4.6")
        self.dep("expat@2.6.4")
        self.tool("meson@1")
        self.tool("ninja@1.13")
        self.tool("pkgconf@3")

    def generate(self):
        PkgConfigDeps(self).generate()
        meson = MesonGenerator(self)
        meson.set_builtin("default_library", "shared" if self.options.shared else "static")
        meson.set_option("documentation", False)
        meson.set_option("tests", False)
        meson.set_option("dtd_validation", False)
        # Cursor themes belong to the machine. The default would be a folder in the package.
        meson.set_option("icon_directory", "/usr/share/icons")
        meson.generate()

    def build(self):
        meson = MesonBuild(self)
        meson.configure()
        meson.build()
        meson.install()

    def _library(self, name: str, requires: list[str]) -> Component:
        component = Component(name, headers=["include"], requires=list(requires))
        if self.options.shared:
            component.shared_libs.append(name)
        else:
            component.static_libs.append(name)
            component.system_libs += ["m", "rt"]
        return component

    def package(self):
        data = {"pkgdatadir": "${prefix}/share/wayland"}
        scanner = Component(
            "wayland-scanner",
            executables=["wayland-scanner"],
            content=["share/wayland"],
            pkg_config_variables=data | {"wayland_scanner": "${prefix}/bin/wayland-scanner"},
        )
        client = self._library("wayland-client", ["libffi"])
        client.pkg_config_variables = data
        components = [
            client,
            self._library("wayland-server", ["libffi"]),
            self._library("wayland-cursor", ["wayland::wayland-client"]),
            self._library("wayland-egl", ["wayland::wayland-client"]),
            scanner,
        ]
        # It talks to the machine's compositor, so the machine's copy is the one to run with
        return Package(components=components, licenses=["COPYING"], system_runtime=True)
