from silo import SiloPackage
from silo.tools.pypi import PyPIInstall


class Meson(SiloPackage):
    """Meson, from PyPI. It starts Ninja."""

    name = "meson"
    version = "1.12.1"
    ignore_settings = ("compiler", "build_type", "cppstd", "libcxx")

    def source(self, src):
        src.empty()

    def deps(self):
        self.tool("ninja@1.13", transitive=True)

    def build(self):
        PyPIInstall(self).install("meson==1.12.1")

    def package(self):
        return PyPIInstall(self).packaged()
