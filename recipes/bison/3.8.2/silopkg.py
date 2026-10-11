import shutil

from silo import Component, Package, SiloPackage


class Bison(SiloPackage):
    """A parser generator that xkbcommon's build runs."""

    name = "bison"
    version = "3.8.2"
    languages = ("c",)

    def source(self, src):
        src.fetch(
            "https://ftp.gnu.org/gnu/bison/bison-3.8.2.tar.xz",
            sha256="9bba0214ccf7f1079c5d59210045227bcf619519840ebfa80cd3849cff5a5bf2",
        )

    def deps(self):
        self.tool("m4@1.4.19", transitive=True)

    def build(self):
        self.build_dir.mkdir(parents=True, exist_ok=True)
        configure = self.source_dir / "configure"
        # Relocatable bison finds its data from where the program sits, and keeps the
        # prefix it was configured with only as the reference. A short one that is not
        # silo's made-up prefix, which would fail the check for a compiled-in path.
        reference_prefix = "/usr"
        self.run(
            [
                "sh",
                configure,
                f"--prefix={reference_prefix}",
                "--enable-relocatable",
                "--disable-nls",
            ],
            cwd=self.build_dir,
            env={"M4": "m4"},
        )
        self.run(["make", "-j8"], cwd=self.build_dir)
        scratch = self.build_dir / "scratch"
        self.run(["make", "install", f"DESTDIR={scratch}"], cwd=self.build_dir)
        target = self.context.stage_dir / self.context.install_prefix.strip("/")
        shutil.copytree(scratch / reference_prefix.strip("/"), target, dirs_exist_ok=True)

    def package(self):
        bison = Component("bison", executables=["bison"], content=["share/bison"])
        return Package(components=[bison], licenses=["COPYING"])
