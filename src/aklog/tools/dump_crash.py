#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function


class DumpCrashLog:
    DEF_PATH_FILE_NAME = "AkCrash"
    DEF_PATH = "~/Desktop/{0}/".format(DEF_PATH_FILE_NAME)

    def __init__(self, platform, is_ndk=False, dir=None, max_size=10):
        self._platform = platform
        self.is_ndk = is_ndk
        self.max_size = max_size
        self.dir = dir

    def do_work(self):
        self._platform.dump_crash_logs(self.is_ndk, self.max_size, self.dir)
