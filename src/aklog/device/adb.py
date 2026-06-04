#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

import os
import subprocess

from aklog.core import cmd_runner, comm_tools
from aklog.core.paths import bundled_tool


class AdbCmd:
    _adb = None

    @staticmethod
    def find_adb(adb_path=None):
        if comm_tools.is_not_empty(AdbCmd._adb):
            return AdbCmd._adb
        _path = None
        if comm_tools.is_empty(adb_path):
            if "ANDROID_HOME" in os.environ:
                name = "adb.exe" if comm_tools.is_windows_os() else "adb"
                path = os.path.join(os.environ["ANDROID_HOME"], "platform-tools", name)
                if os.path.exists(path):
                    _path = path
            if _path is None:
                name = "adb.exe" if comm_tools.is_windows_os() else "adb"
                path = bundled_tool(name)
                if os.path.exists(path):
                    _path = path
        else:
            _path = adb_path

        if not comm_tools.is_exe(_path):
            return None
        AdbCmd._adb = _path
        return AdbCmd._adb


class AdbHelper:
    def __init__(self, device_id=None, adb_path=None, open_log=False):
        self._open_log = open_log
        self._device_id = device_id
        self._adb = AdbCmd.find_adb(adb_path)

    def is_available(self):
        return comm_tools.is_not_empty(self._adb)

    def _base_argv(self):
        if not self.is_available():
            raise OSError("adb not found. Set ANDROID_HOME or place adb in lib/adb")
        argv = [self._adb]
        if comm_tools.is_not_empty(self._device_id):
            argv.extend(["-s", self._device_id])
        return argv

    def _device_argv(self, cmd):
        parts = comm_tools.get_str(cmd).strip().split(" ")
        return self._base_argv() + parts

    def __check_adb_connect(self):
        if not self.is_available():
            return False
        found = False
        for line in cmd_runner.iter_lines(self._base_argv() + ["devices"]):
            if comm_tools.is_empty(line):
                continue
            if line.startswith("List of devices attached"):
                continue
            devices = line.split()
            if len(devices) != 2:
                continue
            serial, status = devices[0], devices[1]
            if status != "device":
                continue
            if comm_tools.is_empty(self._device_id):
                found = True
                break
            if serial == self._device_id:
                found = True
                break
        return found

    def __restart_adb_connect(self):
        base = self._base_argv()
        cmd_runner.run_shell(
            "{0} kill-server && {1} start-server && {2} devices".format(" ".join(base), " ".join(base), " ".join(base)),
            check=False,
        )

    def check_connect(self):
        if self.__check_adb_connect():
            return True
        self.__restart_adb_connect()
        if self.__check_adb_connect():
            return True
        if comm_tools.is_empty(self._device_id):
            raise ValueError("adb: no device connected. Please check USB/debug settings.")
        raise ValueError('adb: device "{0}" not connected.'.format(self._device_id))

    @staticmethod
    def list_connected_devices():
        adb = AdbCmd.find_adb()
        if not adb:
            return []
        result = []
        for line in cmd_runner.iter_lines([adb, "devices"]):
            if comm_tools.is_empty(line) or line.startswith("List of devices attached"):
                continue
            parts = line.split()
            if len(parts) != 2:
                continue
            serial, status = parts[0], parts[1]
            if status == "device":
                result.append(serial)
        return result

    def run_cmd_result_code(self, cmd):
        self.check_connect()
        argv = self._device_argv(cmd)
        if self._open_log:
            print("run {0}".format(" ".join(argv)))
        proc = cmd_runner.popen(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = proc.communicate()
        return proc.returncode, out, err

    def run_cmd(self, cmd):
        code, out, err = self.run_cmd_result_code(cmd)
        if code:
            if self._open_log:
                print("error: {0}".format(comm_tools.get_str(err)))
            raise subprocess.CalledProcessError(code, cmd)
        return comm_tools.get_str(out)

    def cmd_run_iter(self, cmd):
        self.check_connect()
        popen = self.popen(cmd, stdout=subprocess.PIPE, universal_newlines=True)
        for stdout_line in iter(popen.stdout.readline, ""):
            yield comm_tools.get_str(stdout_line)
        popen.stdout.close()
        return_code = popen.wait()
        if return_code:
            raise subprocess.CalledProcessError(return_code, cmd)

    def popen(self, cmd, buf_size=None, stdout=None, stderr=None, universal_newlines=None):
        argv = self._device_argv(cmd)
        if self._open_log:
            print("run {0}".format(" ".join(argv)))
        kw = {}
        if buf_size is not None:
            kw["bufsize"] = buf_size
        if stdout is not None:
            kw["stdout"] = stdout
        if stderr is not None:
            kw["stderr"] = stderr
        if universal_newlines is not None:
            kw["universal_newlines"] = universal_newlines
        return cmd_runner.popen(argv, **kw)
