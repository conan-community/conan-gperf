#!/usr/bin/env python
# -*- coding: utf-8 -*-
from conans import ConanFile


class GperfTestConan(ConanFile):
    settings = 'arch'

    def test(self):
        if 'arm' not in self.settings.arch:
            self.run('gperf --version', run_environment=True)
