#!/usr/bin/env python
# -*- coding: utf-8 -*-
from cpt.packager import ConanMultiPackager
import os
import platform

if __name__ == "__main__":

    arch = os.environ["ARCH"]
    builder = ConanMultiPackager()
    builder.add({"os" : platform.system().replace("Darwin", "Macos"), "arch_build" : arch, "arch": arch}, {}, {}, {})
    builder.run()
