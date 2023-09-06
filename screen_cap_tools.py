#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author:   wswenyue
@date:     2022/11/21 
"""
import datetime
import os.path

import comm_tools
from adb_utils import AdbCmd


class ScreenCapTools(object):
    DEF_PATH_FILE_NAME = "AkScreen"

    def __init__(self, _dir: str = None):
        if comm_tools.is_empty(_dir):
            self._dir_path = comm_tools.get_user_desktop_dir(f"{self.DEF_PATH_FILE_NAME}/")
        else:
            self._dir_path = _dir

    def do_capture(self):
        comm_tools.create_dir_not_exists(self._dir_path)
        pic_name = datetime.datetime.now().strftime("%m%d-%H%M%S-%f.png")
        pic_android_path = f"/sdcard/{pic_name}"
        pic_local_path = os.path.join(self._dir_path, pic_name)
        adb = AdbCmd.find_adb()
        os.system(f"{adb} shell screencap -p {pic_android_path} ")
        os.system(f"{adb} pull {pic_android_path} {pic_local_path}")
        os.system(f"{adb} shell rm {pic_android_path}")
        print("succeed.")
        if comm_tools.is_mac_os():
            os.system(f"open {pic_local_path}")

#
# if __name__ == '__main__':
#     ScreenCapTools().do_capture()
