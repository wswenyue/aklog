#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

import threading
import time

from aklog.core import comm_tools


class AppInfoHelper:
    _instance = None
    _data_lock = threading.Lock()

    def __init__(self, platform):
        self._platform = platform
        self._main_process = {}
        self._children_process = {}
        self._cur_app_package = ""

    @classmethod
    def start(cls, platform, delay=3):
        cls._instance = AppInfoHelper(platform)
        comm_tools.new_thread(cls._instance._run, name="Thread-FetchAPKInfo", args=(delay,))

    @classmethod
    def get_instance(cls):
        return cls._instance

    @staticmethod
    def cur_app_package():
        inst = AppInfoHelper._instance
        if inst is None:
            return ""
        with AppInfoHelper._data_lock:
            return comm_tools.get_str(inst._cur_app_package)

    @staticmethod
    def found_name_by_pid(pid):
        inst = AppInfoHelper._instance
        if inst is None:
            return None
        with AppInfoHelper._data_lock:
            if pid in inst._main_process:
                return inst._main_process[pid]
            if pid in inst._children_process:
                return inst._children_process[pid]
        return None

    @staticmethod
    def is_main_process(pid):
        name = AppInfoHelper.found_name_by_pid(pid)
        if not name:
            return None
        if ":" in name:
            return False
        return True

    def _refresh_processes(self):
        try:
            process = {}
            for pid, name in self._platform.iter_processes():
                process[pid] = name
            with AppInfoHelper._data_lock:
                self._children_process.clear()
                self._main_process.clear()
                for pid, name in process.items():
                    if ":" in name:
                        self._children_process[pid] = name
                    else:
                        self._main_process[pid] = name
        except Exception as e:
            print("{0}".format(e))

    def _refresh_foreground_package(self):
        try:
            pkg = self._platform.get_foreground_package()
            if comm_tools.is_not_empty(pkg):
                with AppInfoHelper._data_lock:
                    self._cur_app_package = pkg
        except Exception as e:
            print("get_cur_app_package Error==>{0}".format(e))

    def _run(self, delay):
        while True:
            self._refresh_processes()
            self._refresh_foreground_package()
            time.sleep(int(delay))
