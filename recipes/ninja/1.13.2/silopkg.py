from silo import SiloPackage
from silo.tools.pypi import PyPIInstall


class Ninja(SiloPackage):
    """Ninja, from the wheel on PyPI."""

    name = "ninja"
    version = "1.13.2"
    ignore_settings = ("compiler", "build_type", "cppstd", "libcxx")

    def source(self, src):
        src.empty()

    def build(self):
        PyPIInstall(self).install("ninja==1.13.2")

    def package(self):
        return PyPIInstall(self).packaged()
