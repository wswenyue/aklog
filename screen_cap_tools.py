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
from hdc_cmd import HdcCmd


class ScreenCapTools(object):
    DEF_PATH_FILE_NAME = "AkScreen"
    def_screen_cap_path = f"~/Desktop/{DEF_PATH_FILE_NAME}/"

    def __init__(self, _dir: str = None, is_harmonyos: bool = False):
        self._is_harmonyos = is_harmonyos
        if comm_tools.is_empty(_dir):
            self._dir_path = comm_tools.get_user_desktop_dir(f"{self.DEF_PATH_FILE_NAME}/")
        else:
            self._dir_path = _dir

    def get_phone_cap_dir(self) -> str:
        if self._is_harmonyos:
            return f"/data/local/tmp/"
        return f"/sdcard/"

    def do_capture(self):
        comm_tools.create_dir_not_exists(self._dir_path)
        pic_name = datetime.datetime.now().strftime("%m%d-%H%M%S-%f.png")
        pic_local_path = os.path.join(self._dir_path, pic_name)
        pic_phone_path = os.path.join(self.get_phone_cap_dir(), pic_name)
        if self._is_harmonyos:
            hdc = HdcCmd.find_hdc()
            os.system(f"{hdc} shell snapshot_display -f {pic_phone_path} ")
            os.system(f"{hdc} file recv {pic_phone_path} {pic_local_path}")
            os.system(f"{hdc} shell rm {pic_phone_path}")
        else:
            adb = AdbCmd.find_adb()
            os.system(f"{adb} shell screencap -p {pic_phone_path} ")
            os.system(f"{adb} pull {pic_phone_path} {pic_local_path}")
            os.system(f"{adb} shell rm {pic_phone_path}")
        print("succeed.")
        if comm_tools.is_mac_os():
            os.system(f"open {pic_local_path}")

#
# if __name__ == '__main__':
#     ScreenCapTools().do_capture()
