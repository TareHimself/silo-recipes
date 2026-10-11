from silo import SiloPackage
from silo.tools.pypi import PyPIInstall


class Conan(SiloPackage):
    """Conan, from PyPI."""

    name = "conan"
    version = "2.33.0"
    ignore_settings = ("compiler", "build_type", "cppstd", "libcxx")

    def source(self, src):
        src.empty()

    def build(self):
        PyPIInstall(self).install("conan==2.33.0")

    def package(self):
        return PyPIInstall(self).packaged()
