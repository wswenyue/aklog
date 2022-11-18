#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author:   wswenyue
@date:     2022/11/9 
"""
import threading
import time
from typing import Optional

import comm_tools
from adb_utils import AdbHelper
from comm_tools import is_empty, new_thread


class AppInfoHelper(object):
    _data_lock = threading.Lock()
    _main_process = {}
    _children_process = {}
    _cur_app_package = None

    @staticmethod
    def cur_app_package():
        if comm_tools.is_empty(AppInfoHelper._cur_app_package):
            return ""
        return comm_tools.get_str(AppInfoHelper._cur_app_package)

    @staticmethod
    def found_name_by_pid(pid: str) -> Optional[str]:
        if pid in AppInfoHelper._main_process.keys():
            return AppInfoHelper._main_process[pid]
        if pid in AppInfoHelper._children_process.keys():
            return AppInfoHelper._children_process[pid]
        return None

    @staticmethod
    def is_main_process(pid: str) -> Optional[bool]:
        name = AppInfoHelper.found_name_by_pid(pid)
        if not name:
            return None
        if ":" in name:
            return False
        return True

    @staticmethod
    def _print():
        with AppInfoHelper._data_lock:
            print(f"=========main======={AppInfoHelper._cur_app_package}=======")
            for pid, name in AppInfoHelper._main_process.items():
                print(f"{pid}\t\t{name}")
            print("=========main===end===========")
            print("=========children==============")
            for pid, name in AppInfoHelper._children_process.items():
                print(f"{pid}\t\t{name}")
            print("=========children===end===========")

    @staticmethod
    def _get_parser_process_info():
        # print(f"=========get_parser_process_info==============")
        try:
            process = {}
            is_skip_title = True
            for line in AdbHelper().cmd_run_iter("shell ps"):
                if is_skip_title or is_empty(line):
                    is_skip_title = False
                    continue
                # print(f"=>{line}<=")
                ls = line.strip().split()
                if len(ls) != 9:
                    raise ValueError(f"parser Error={len(ls)}=>" + line)
                # USER      PID   PPID  VSIZE  RSS   WCHAN              PC  NAME
                user = ls[0]
                pid = ls[1]
                name = ls[-1]
                if not user.startswith("u0_") \
                        or ("/" in name) \
                        or ("[" in name) \
                        or ("]" in name):
                    # print("=ignore=>" + line)
                    pass
                else:
                    process[pid] = name

            with AppInfoHelper._data_lock:
                AppInfoHelper._children_process.clear()
                AppInfoHelper._main_process.clear()
                for pid, name in process.items():
                    if ":" in name:
                        # 子进程
                        AppInfoHelper._children_process[pid] = name
                    else:
                        # 主进程
                        AppInfoHelper._main_process[pid] = name
        except Exception as e:
            print(f"{e}")

    @staticmethod
    def _get_cur_app_package():
        try:
            for line in AdbHelper().cmd_run_iter("shell dumpsys window windows | grep -E 'mFocusedApp'"):
                line = line.strip()
                if line.startswith("mFocusedApp="):
                    AppInfoHelper._cur_app_package = line.split()[4].split("/")[0]
                    break
        except Exception as e:
            print(f"get_cur_app_package Error==>{e}")

    @staticmethod
    def start():
        new_thread(AppInfoHelper.__run, name="Thread-FetchAPKInfo", args=(3,))

    @staticmethod
    def __run(delay):
        while True:
            AppInfoHelper._get_parser_process_info()
            AppInfoHelper._get_cur_app_package()
            # AppInfoHelper.print()
            time.sleep(int(delay))

#
# if __name__ == '__main__':
#     AppInfoHelper.start()
#     time.sleep(1000)
