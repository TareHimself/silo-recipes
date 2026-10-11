from silo import Component, Package, SiloPackage


class M4(SiloPackage):
    """A macro processor that bison runs."""

    name = "m4"
    version = "1.4.19"
    languages = ("c",)

    def source(self, src):
        src.fetch(
            "https://ftpmirror.gnu.org/m4/m4-1.4.19.tar.xz",
            sha256="63aede5c6d33b6d9b13511cd0be2cac046f2e70fd0a07aa9573a04a82783af96",
        )

    def build(self):
        self.build_dir.mkdir(parents=True, exist_ok=True)
        configure = self.source_dir / "configure"
        prefix = self.context.install_prefix
        self.run(["sh", configure, f"--prefix={prefix}", "--disable-nls"], cwd=self.build_dir)
        self.run(["make", "-j8"], cwd=self.build_dir)
        self.run(["make", "install", f"DESTDIR={self.context.stage_dir}"], cwd=self.build_dir)

    def package(self):
        return Package(components=[Component("m4", executables=["m4"])], licenses=["COPYING"])
