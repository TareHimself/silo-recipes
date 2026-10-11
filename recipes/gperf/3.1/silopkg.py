from silo import Component, Package, SiloPackage


class Gperf(SiloPackage):
    """A code generator that fontconfig's build runs."""

    name = "gperf"
    version = "3.1"

    def source(self, src):
        src.fetch(
            "https://ftpmirror.gnu.org/gperf/gperf-3.1.tar.gz",
            sha256="588546b945bba4b70b6a3a616e80b4ab466e3f33024a352fc2198112cdbb3ae2",
        )

    def build(self):
        self.build_dir.mkdir(parents=True, exist_ok=True)
        configure = self.source_dir / "configure"
        prefix = self.context.install_prefix
        # gperf 3.1 uses the register keyword, which C++17 removed
        flags = {"CXXFLAGS": "-O2 -std=gnu++14"}
        self.run(["sh", configure, f"--prefix={prefix}"], cwd=self.build_dir, env=flags)
        self.run(["make", "-j8"], cwd=self.build_dir)
        self.run(["make", "install", f"DESTDIR={self.context.stage_dir}"], cwd=self.build_dir)

    def package(self):
        return Package(components=[Component("gperf", executables=["gperf"])], licenses=["COPYING"])
