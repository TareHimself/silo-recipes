from silo import Component, Package, SiloPackage
from silo.enums import Platform
from silo.tools.cmake import CMakeBuild, CMakeGenerator
from silo.tools.pkgconfig import PkgConfigDeps
from silo.tools.pkgconfig.pkg_config_deps import PC_DIR


class Glfw(SiloPackage):
    """Windows and input. On Linux it talks to Wayland only."""

    name = "glfw"
    version = "3.4"
    languages = ("c",)

    def source(self, src):
        src.git(
            "https://github.com/glfw/glfw.git",
            commit="7b6aead9fb88b3623e3b3725ebb42670cbe4c579",
        )

    def deps(self):
        if self.profile.settings.os is Platform.Linux:
            self.dep("wayland@1.22.0")
            self.dep("wayland-protocols@1.36")
            self.dep("xkbcommon@1.6.0")
            self.tool("wayland@1.22.0")
            self.tool("pkgconf@3")
        self.tool("cmake@4.3")

    def generate(self):
        if self.profile.settings.os is Platform.Linux:
            PkgConfigDeps(self).generate()
        toolchain = CMakeGenerator(self)
        for option in ("EXAMPLES", "TESTS", "DOCS"):
            toolchain.add_cache_bool(f"GLFW_BUILD_{option}", False)
        toolchain.add_cache_bool("GLFW_INSTALL", True)
        toolchain.add_cache_bool("BUILD_SHARED_LIBS", False)
        toolchain.add_cache_bool("GLFW_BUILD_X11", False)
        toolchain.add_cache_bool("GLFW_BUILD_WAYLAND", True)
        toolchain.generate()

    def build(self):
        if self.profile.settings.os is Platform.Linux:
            self.env["PKG_CONFIG_LIBDIR"] = str(self.context.generated_dir / PC_DIR)
        cmake = CMakeBuild(self)
        cmake.configure()
        cmake.build()
        cmake.install()

    def package(self):
        library = Component("glfw", headers=["include"], static_libs=["glfw3"])
        if self.profile.settings.os is Platform.Windows:
            library.system_libs += ["gdi32", "user32", "shell32"]
        elif self.profile.settings.os is Platform.Linux:
            library.system_libs += ["m", "pthread", "dl", "rt"]
            library.requires += [
                "wayland::wayland-client",
                "wayland::wayland-cursor",
                "wayland::wayland-egl",
                "xkbcommon",
            ]
        else:
            library.frameworks += ["Cocoa", "IOKit", "CoreFoundation", "QuartzCore"]
        return Package(components=[library], licenses=["LICENSE.md"])
