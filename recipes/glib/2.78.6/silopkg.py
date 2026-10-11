from silo import Component, Package, SiloPackage
from silo.tools.meson import MesonBuild, MesonGenerator
from silo.tools.pkgconfig import PkgConfigDeps

TOOLS = ["glib-mkenums", "glib-genmarshal"]


class Glib(SiloPackage):
    name = "glib"
    version = "2.78.6"
    languages = ("c",)

    def source(self, src):
        src.fetch(
            "https://download.gnome.org/sources/glib/2.78/glib-2.78.6.tar.xz",
            sha256="244854654dd82c7ebcb2f8e246156d2a05eb9cd1ad07ed7a779659b4602c9fae",
        )

    def patch(self, src):
        # distutils left Python in 3.12. The versions compared here are plain numbers.
        codegen = "gio/gdbus-2.0/codegen/utils.py"
        src.replace(codegen, "import distutils.version", "")
        src.replace(
            codegen,
            "distutils.version.LooseVersion(v)",
            '[int(part) if part.isdigit() else part for part in v.split(".")]',
        )

    def deps(self):
        self.dep("libffi@3.4.6")
        self.dep("pcre2@10.44")
        self.dep("zlib@1.3.1")
        self.tool("meson@1")
        self.tool("pkgconf@3")

    def generate(self):
        PkgConfigDeps(self, aliases={"libpcre2-8": "pcre2::pcre2-8"}).generate()
        meson = MesonGenerator(self)
        # glib compiles these folders in. They belong to the machine, not to this package.
        meson.set_builtin("localstatedir", "/var")
        meson.set_builtin("datadir", "/usr/share")
        meson.set_builtin("libexecdir", "/usr/libexec")
        meson.set_option("runtime_dir", "/run")
        meson.set_option("charsetalias_dir", "/usr/lib")
        # Nowhere, so a plugin built for the machine's own glib is never loaded into this one
        meson.set_option("gio_module_dir", "/var/empty/gio-modules")
        meson.set_option("tests", False)
        meson.set_option("xattr", False)
        meson.set_option("glib_debug", "disabled")
        for feature in ("selinux", "libmount", "nls", "libelf", "sysprof"):
            meson.set_option(feature, "disabled")
        meson.generate()

    def build(self):
        meson = MesonBuild(self)
        meson.configure()
        meson.build()
        meson.install()

    def package(self):
        glib = Component(
            "glib-2.0",
            headers=["include/glib-2.0", "lib/glib-2.0/include"],
            static_libs=["glib-2.0"],
            executables=TOOLS,
            requires=["pcre2"],
            system_libs=["m", "pthread"],
        )
        gmodule = Component("gmodule-2.0", static_libs=["gmodule-2.0"], requires=["glib::glib-2.0"])
        gobject = Component(
            "gobject-2.0", static_libs=["gobject-2.0"], requires=["glib::glib-2.0", "libffi"]
        )
        gio = Component(
            "gio-2.0",
            headers=["include/gio-unix-2.0"],
            static_libs=["gio-2.0"],
            requires=["glib::gobject-2.0", "glib::gmodule-2.0", "zlib"],
            system_libs=["resolv"],
        )
        return Package(components=[glib, gmodule, gobject, gio], licenses=["COPYING"])
