#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
see : https://www.cnblogs.com/liuzhipenglove/p/7063808.html
@author:   wswenyue
@date:     2022/9/7 
"""
import os
import subprocess
import threading

from comm_tools import is_windows_os, is_exe, cmd_run_iter, is_empty, get_str


class AdbHelper(object):
    _instance_lock = threading.Lock()

    @classmethod
    def instance(cls, *args, **kwargs):
        if not hasattr(AdbHelper, "_instance"):
            with AdbHelper._instance_lock:
                if not hasattr(AdbHelper, "_instance"):
                    AdbHelper._instance = AdbHelper(*args, **kwargs)
        return AdbHelper._instance

    def __init__(self, adb_path=None, open_log=False):
        self._open_log = open_log
        self._adb = adb_path
        self.__find_adb()

    def __find_adb(self):
        if not self._adb:
            if "ANDROID_HOME" in os.environ:
                if is_windows_os():
                    path = os.path.join(os.environ["ANDROID_HOME"], "platform-tools", "adb.exe")
                    if os.path.exists(path):
                        self._adb = path
                    else:
                        raise EnvironmentError(
                            "Adb not found in $ANDROID_HOME path: %s." % os.environ["ANDROID_HOME"])
                else:
                    path = os.path.join(os.environ["ANDROID_HOME"], "platform-tools", "adb")
                    if os.path.exists(path):
                        self._adb = path
                    else:
                        raise EnvironmentError(
                            "Adb not found in $ANDROID_HOME path: %s." % os.environ["ANDROID_HOME"])
            else:
                raise EnvironmentError(
                    "Adb not found in $ANDROID_HOME path: %s." % os.environ["ANDROID_HOME"])
        if not is_exe(self._adb):
            raise ValueError(f"the {self._adb} is not executable file!!!")

    def __check_adb_connect(self):
        _cmd = f"{self._adb} devices"
        for line in cmd_run_iter(_cmd):
            if is_empty(line):
                continue
            if line.startswith("List of devices attached"):
                continue
            devices = line.split()
            if len(devices) != 2:
                raise ValueError(f"run {_cmd} ;; devices result error!!!")
            if devices[1] == "device":
                return True
        return False

    def __restart_adb_connect(self):
        _cmd = f"{self._adb} kill-server && {self._adb} server && {self._adb} devices"
        os.system(_cmd)

    def check_connect(self):
        if self.__check_adb_connect():
            return True
        self.__restart_adb_connect()
        if self.__check_adb_connect():
            return True
        raise ValueError("adb not connection!!! Please check!!!")

    def run_cmd(self, cmd) -> str:
        self.check_connect()
        _cmd = f"{self._adb} {cmd}"
        if self._open_log:
            print(f"run {_cmd}")
        process = subprocess.Popen(str(_cmd).split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = process.communicate()
        if process.returncode:
            raise subprocess.CalledProcessError(process.returncode, cmd)
        return get_str(out)

    def cmd_run_iter(self, cmd):
        self.check_connect()
        popen = self.popen(cmd, stdout=subprocess.PIPE, universal_newlines=True)
        for stdout_line in iter(popen.stdout.readline, ""):
            yield get_str(stdout_line)
        popen.stdout.close()
        return_code = popen.wait()
        if return_code:
            raise subprocess.CalledProcessError(return_code, cmd)

    def popen(self, cmd, buf_size=None,
              stdout=None, stderr=None,
              universal_newlines=None) -> subprocess.Popen:
        _cmd = f"{self._adb} {cmd}"
        if self._open_log:
            print(f"run {_cmd}")
        return subprocess.Popen(str(_cmd).split(), bufsize=buf_size, stdout=stdout, stderr=stderr,
                                universal_newlines=universal_newlines)
