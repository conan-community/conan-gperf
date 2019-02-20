#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from conans import ConanFile, tools, AutoToolsBuildEnvironment


class GperfConan(ConanFile):
    name = "gperf"
    version = "3.1"
    license = "GPL-3.0"
    url = "https://github.com/conan-community/conan-gperf"
    homepage = "https://www.gnu.org/software/gperf"
    description = "GNU gperf is a perfect hash function generator"
    topics = ("conan", "gperf", "hash-generator", "hash")
    author = "Conan Community"
    settings = "os_build", "arch_build", "compiler"
    exports = "LICENSE.md"
    _source_subfolder = "source_subfolder"
    _autotools = None

    @property
    def _is_msvc(self):
        return self.settings.compiler == "Visual Studio"

    @property
    def _is_mingw_windows(self):
        return self.settings.os_build == "Windows" and self.settings.compiler == "gcc" and os.name == "nt"

    def build_requirements(self):
        if self.settings.os_build == "Windows":
            self.build_requires("cygwin_installer/2.9.0@bincrafters/stable")

    def source(self):
        sha256 = "588546b945bba4b70b6a3a616e80b4ab466e3f33024a352fc2198112cdbb3ae2"
        tools.get("https://ftp.gnu.org/pub/gnu/gperf/gperf-{}.tar.gz".format(self.version), sha256=sha256)
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_autotools(self):
        if not self._autotools:
            args = []
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
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        with tools.chdir(self._source_subfolder):
            autotools = self._configure_autotools()
            autotools.install()
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_id(self):
        del self.info.settings.compiler

    def package_info(self):
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
