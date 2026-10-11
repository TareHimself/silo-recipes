from silo import Component, Package, SiloPackage
from silo.enums import Platform
from silo.tools.cmake import CMakeBuild, CMakeDeps, CMakeGenerator


class VulkanLoader(SiloPackage):
    name = "vulkan-loader"
    version = "1.3.296"
    languages = ("c",)

    def source(self, src):
        src.git(
            "https://github.com/KhronosGroup/Vulkan-Loader.git",
            commit="7aeb5e4324957b6f60dac5c8cedb955df4fecbfb",
        )

    def patch(self, src):
        # Upstream asks for the headers by a package name silo does not write
        src.replace(
            "CMakeLists.txt",
            "find_package(VulkanHeaders CONFIG QUIET)",
            "find_package(Vulkan CONFIG REQUIRED)",
        )

    def deps(self):
        self.dep("vulkan-headers@1.3.296")
        self.tool("cmake@4.3")
        self.tool("pkgconf@3")
        self.tool("ninja@1.13")

    def generate(self):
        deps = CMakeDeps(self)
        deps.alias("Vulkan::Headers", "vulkan-headers::vulkan-headers")
        deps.generate()
        toolchain = CMakeGenerator(self)
        toolchain.add_cache_bool("BUILD_TESTS", False)
        toolchain.add_cache_string("SYSCONFDIR", "/etc")
        # The machine's own loader is the one that runs, so window systems are not built in
        for system in ("XCB", "XLIB", "WAYLAND"):
            toolchain.add_cache_bool(f"BUILD_WSI_{system}_SUPPORT", False)
        toolchain.generate()

    def build(self):
        cmake = CMakeBuild(self)
        cmake.configure()
        cmake.build()
        cmake.install()

    def package(self):
        # Drivers find the loader by this file name, so it is always a shared library
        library = "vulkan-1" if self.profile.settings.os is Platform.Windows else "vulkan"
        loader = Component("vulkan-loader", shared_libs=[library], requires=["vulkan-headers"])
        # The graphics driver installs the loader that matches it
        return Package(components=[loader], licenses=["LICENSE.txt"], system_runtime=True)
