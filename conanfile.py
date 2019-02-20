#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from conans import ConanFile, tools, AutoToolsBuildEnvironment


class GperfConan(ConanFile):
    name = "gperf"
    version = "3.1"
    license = "GNU GPL v4"
    url = "https://github.com/conan-community/conan-gperf"
    homepage = "https://www.gnu.org/software/gperf/"
    description = "GNU gperf is a perfect hash function generator"
    topics = ("conan", "gperf", "hash-generator", "hash")
    author = "Conan Community"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    exports = "LICENSE.md"
    _source_subfolder = "source_subfolder"
    _autotools = None

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx

    @property
    def _is_msvc(self):
        return self.settings.compiler == "Visual Studio"

    @property
    def _is_mingw_windows(self):
        return self.settings.os == "Windows" and self.settings.compiler == "gcc" and os.name == "nt"

    def build_requirements(self):
        if self.settings.os == "Windows":
            self.build_requires("cygwin_installer/2.9.0@bincrafters/stable")

    def source(self):
        tools.get("http://ftp.gnu.org/pub/gnu/gperf/gperf-{}.tar.gz".format(self.version))
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_autotools(self):
        if not self._autotools:
            args = []
            if self.options.shared:
                args.extend(["--enable-shared", "--disable-static"])
            else:
                args.extend(["--enable-static", "--disable-shared"])
            if self.settings.build_type == "Debug":
                args.append("--enable-debug")

            cwd = os.getcwd()
            win_bash = self._is_msvc or self._is_mingw_windows
            if self._is_msvc:
                args.extend(["CC={}/build-aux/compile cl -nologo".format(cwd),
                                "CFLAGS=-{}".format(self.settings.compiler.runtime),
                                "CXX={}/build-aux/compile cl -nologo".format(cwd),
                                "CXXFLAGS=-{}".format(self.settings.compiler.runtime),
                                "CPPFLAGS=-D_WIN32_WINNT=_WIN32_WINNT_WIN8 -I/usr/local/msvc32/include",
                                "LDFLAGS=-L/usr/local/msvc32/lib",
                                "LD=link",
                                "NM=dumpbin -symbols",
                                "STRIP=:",
                                "AR={}/build-aux/ar-lib lib".format(cwd),
                                "RANLIB=:"])

            self._autotools = AutoToolsBuildEnvironment(self, win_bash=win_bash)
            self._autotools.configure(args=args)
        return self._autotools

    def _build_configure(self):
        with tools.chdir(self._source_subfolder):
            autotools = self._configure_autotools()
            autotools.make()

    def build(self):
        if self._is_msvc:
            with tools.vcvars(self.settings):
                self._build_configure()
        else:
            self._build_configure()

    def package(self):
        with tools.chdir(self._source_subfolder):
            autotools = self._configure_autotools()
            autotools.install()

    def package_info(self):
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
