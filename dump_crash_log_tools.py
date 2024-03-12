#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
拉取手机crash日志
@author:   wswenyue
@date:     2024/3/8
"""
import os
import time
from io import StringIO

import comm_tools
from adb_utils import AdbHelper


class DumpCrashLog(object):
    DEF_PATH_FILE_NAME = "AkCrash"
    DEF_PATH = f"~/Desktop/{DEF_PATH_FILE_NAME}/"

    def __init__(self, is_ndk: bool = False, dir: str = None, max_size: int = 10):
        """
        :param is_ndk: 是否打印ndk日志，默认是false，既打印app日志
        :param dir:
        :param max_size: 最大打印日志数量
        """
        self.is_ndk = is_ndk
        self.max_size = max_size
        if is_ndk:
            self.filter_tag = "data_app_native_crash"
            self.logName = "native_" + time.strftime("%Y%m%d%H%M%S", time.localtime()) + ".log"
        else:
            self.filter_tag = "data_app_crash"
            self.logName = "app_" + time.strftime("%Y%m%d%H%M%S", time.localtime()) + ".log"

        if comm_tools.is_empty(dir):
            self.log_save_path = os.path.join(comm_tools.get_user_desktop_dir(f"{self.DEF_PATH_FILE_NAME}/"),
                                              self.logName)
        else:
            self.log_save_path = os.path.join(dir, self.logName)

    def do_work(self):
        time_list = []
        for line in AdbHelper().cmd_run_iter("shell dumpsys dropbox"):
            if comm_tools.is_empty(line):
                continue
            if self.filter_tag not in line:
                continue
            _time = line.split(self.filter_tag, 1)[0].strip()
            # print(f"time-->${_time}<--")
            time_list.append(_time)

        if len(time_list) <= 0:
            print(f"not found any log for {self.filter_tag}")
            return
        buf = StringIO()
        tip_begin = f"##########begin######total found:{len(time_list)} ;max:{self.max_size}#####################\n"
        tip_end = f"############end######total found:{len(time_list)} ;max:{self.max_size}#####################\n"
        tip_newline = "\n----------------------------------------------------------------\n"
        buf.write(tip_begin)
        print(tip_begin)
        for index, t in enumerate(reversed(time_list)):
            out = AdbHelper().run_cmd(f"shell dumpsys dropbox --print '{t}'")
            buf.write(out)
            buf.write(tip_newline)
            print(out)
            print(tip_newline)
            if index >= self.max_size - 1:
                break
        buf.write(tip_end)
        print(tip_end)
        comm_tools.write_to_file_no_error(buf.getvalue(), self.log_save_path)

#
# if __name__ == '__main__':
#     DumpCrashLog().do_work()
