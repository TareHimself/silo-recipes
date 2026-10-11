from silo import SiloPackage
from silo.tools.pypi import PyPIInstall


class Pkgconf(SiloPackage):
    """pkgconf, from the wheel on PyPI."""

    name = "pkgconf"
    version = "3.0.7"
    ignore_settings = ("compiler", "build_type", "cppstd", "libcxx")

    def source(self, src):
        src.empty()

    def build(self):
        PyPIInstall(self).install("pkgconf==3.0.7.post0")

    def package(self):
        return PyPIInstall(self).packaged(bin_dir="pkgconf/.bin")
