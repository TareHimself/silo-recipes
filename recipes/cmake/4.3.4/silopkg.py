from silo import SiloPackage
from silo.tools.pypi import PyPIInstall


class CMake(SiloPackage):
    """CMake, from the wheel on PyPI. It starts Ninja."""

    name = "cmake"
    version = "4.3.4"
    ignore_settings = ("compiler", "build_type", "cppstd", "libcxx")

    def source(self, src):
        src.empty()

    def deps(self):
        self.tool("ninja@1.13", transitive=True)

    def build(self):
        PyPIInstall(self).install("cmake==4.3.4")

    def package(self):
        return PyPIInstall(self).packaged(["cmake", "ctest", "cpack"], bin_dir="cmake/data/bin")
