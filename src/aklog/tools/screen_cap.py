#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

import datetime
import os

from aklog.core import comm_tools


class ScreenCapTools:
    DEF_PATH_FILE_NAME = "AkScreen"
    def_screen_cap_path = "~/Desktop/{0}/".format(DEF_PATH_FILE_NAME)

    def __init__(self, platform, _dir=None):
        self._platform = platform
        if comm_tools.is_empty(_dir):
            self._dir_path = comm_tools.get_user_desktop_dir("{0}/".format(self.DEF_PATH_FILE_NAME))
        else:
            self._dir_path = _dir

    def do_capture(self):
        comm_tools.create_dir_not_exists(self._dir_path)
        ext = self._platform.screen_cap_ext()
        pic_name = datetime.datetime.now().strftime("%m%d-%H%M%S-%f") + ext
        pic_local_path = os.path.join(self._dir_path, pic_name)
        pic_phone_path = os.path.join(self._platform.phone_tmp_dir(), pic_name)
        self._platform.capture_screen(pic_phone_path, pic_local_path)
        print("succeed.")
        if comm_tools.is_mac_os():
            os.system("open {0}".format(pic_local_path))
