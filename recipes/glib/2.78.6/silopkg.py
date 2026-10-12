from silo import Component, Package, SiloPackage
from silo.enums import Platform
from silo.tools.meson import MesonBuild, MesonGenerator
from silo.tools.pkgconfig import PkgConfigDeps

# Python scripts, named by path because they have no .exe on Windows
TOOLS = ["bin/glib-mkenums", "bin/glib-genmarshal"]


class Glib(SiloPackage):
    name = "glib"
    version = "2.78.6"
    languages = ("c",)

    def source(self, src):
        src.fetch(
            "https://download.gnome.org/sources/glib/2.78/glib-2.78.6.tar.xz",
            sha256="244854654dd82c7ebcb2f8e246156d2a05eb9cd1ad07ed7a779659b4602c9fae",
        )

    @property
    def needs_intl(self) -> bool:
        """Whether gettext has to come from a package: only glibc has it."""
        linux = self.profile.settings.os is Platform.Linux
        return not linux or "musl" in self.profile.compiler.target

    def patch(self, src):
        if self.needs_intl:
            # Meson looks for "intl" in the C library and on the machine only, never through
            # pkg-config, so the package is asked for under another name
            src.replace(
                "meson.build",
                "libintl = dependency('intl', required: false)",
                "libintl = dependency('libintl', required: false)",
            )
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
        if self.needs_intl:
            self.dep("proxy-libintl@0.4")
        self.tool("meson@1")
        self.tool("pkgconf@3")

    def generate(self):
        aliases = {"libpcre2-8": "pcre2::pcre2-8"}
        if self.needs_intl:
            aliases["libintl"] = "proxy-libintl::intl"
        PkgConfigDeps(self, aliases=aliases).generate()
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
        windows = self.profile.settings.os is Platform.Windows
        macos = self.profile.settings.os is Platform.Darwin
        system_libs = ["ws2_32", "winmm"] if windows else ["m", "pthread"]
        if macos:
            # Character set conversion is in the C library on Linux and a library here
            system_libs.append("iconv")
        glib = Component(
            "glib-2.0",
            headers=["include/glib-2.0", "lib/glib-2.0/include"],
            static_libs=["glib-2.0"],
            executables=TOOLS,
            requires=["pcre2", "proxy-libintl"] if self.needs_intl else ["pcre2"],
            system_libs=system_libs,
            frameworks=["CoreFoundation", "Foundation", "Carbon"] if macos else [],
        )
        gmodule = Component("gmodule-2.0", static_libs=["gmodule-2.0"], requires=["glib::glib-2.0"])
        gobject = Component(
            "gobject-2.0", static_libs=["gobject-2.0"], requires=["glib::glib-2.0", "libffi"]
        )
        gio = Component(
            "gio-2.0",
            headers=["include/gio-win32-2.0" if windows else "include/gio-unix-2.0"],
            static_libs=["gio-2.0"],
            requires=["glib::gobject-2.0", "glib::gmodule-2.0", "zlib"],
            system_libs=["shlwapi", "dnsapi", "iphlpapi", "ws2_32"] if windows else ["resolv"],
            frameworks=["AppKit"] if macos else [],
        )
        return Package(components=[glib, gmodule, gobject, gio], licenses=["COPYING"])
