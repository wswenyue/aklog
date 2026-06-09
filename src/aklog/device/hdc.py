#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

import os
import subprocess

from aklog.core import cmd_runner, comm_tools
from aklog.core.paths import bundled_tool


class HdcCmd:
    _hdc = None

    @staticmethod
    def find_hdc(hdc_path=None):
        if comm_tools.is_not_empty(HdcCmd._hdc):
            return HdcCmd._hdc
        _path = None
        if comm_tools.is_empty(hdc_path):
            if "HARMONY_HOME" in os.environ:
                pattern = (
                    "/sdk/*/openharmony/toolchains/hdc.exe"
                    if comm_tools.is_windows_os()
                    else "/sdk/*/openharmony/toolchains/hdc"
                )
                path = comm_tools.find_file(pattern, os.environ["HARMONY_HOME"])
                if path and os.path.exists(path):
                    _path = path
            if _path is None:
                name = "hdc.exe" if comm_tools.is_windows_os() else "hdc"
                path = bundled_tool(name)
                if os.path.exists(path):
                    _path = path
        else:
            _path = hdc_path

        if not comm_tools.is_exe(_path):
            return None
        HdcCmd._hdc = _path
        return HdcCmd._hdc


class HdcHelper:
    def __init__(self, device_id=None, hdc_path=None, open_log=False):
        self._open_log = open_log
        self._device_id = device_id
        self._hdc = HdcCmd.find_hdc(hdc_path)

    def is_available(self):
        return comm_tools.is_not_empty(self._hdc)

    def _base_argv(self):
        if not self.is_available():
            raise OSError("hdc not found. Set HARMONY_HOME or place hdc in lib/hdc")
        return [self._hdc]

    def _target_argv(self, cmd):
        parts = comm_tools.get_str(cmd).strip().split(" ")
        argv = self._base_argv()
        if comm_tools.is_not_empty(self._device_id):
            argv.extend(["-t", self._device_id])
        return argv + parts

    def __check_connect(self):
        if not self.is_available():
            return False
        for line in cmd_runner.iter_lines(self._base_argv() + ["list", "targets"]):
            if comm_tools.is_empty(line):
                continue
            line = line.strip()
            if line == "[Empty]":
                return False
            if comm_tools.is_empty(self._device_id):
                return True
            if line == self._device_id or line.startswith(self._device_id):
                return True
        return False

    def __restart_connect(self):
        base = " ".join(self._base_argv())
        cmd_runner.run_shell("{0} kill -r && {1} list targets -v".format(base, base), check=False)

    def check_connect(self):
        if self.__check_connect():
            return True
        self.__restart_connect()
        if self.__check_connect():
            return True
        if comm_tools.is_empty(self._device_id):
            raise ValueError("hdc: no device connected. Please check USB/debug settings.")
        raise ValueError('hdc: device "{0}" not connected.'.format(self._device_id))

    @staticmethod
    def list_connected_devices():
        hdc = HdcCmd.find_hdc()
        if not hdc:
            return []
        result = []
        for line in cmd_runner.iter_lines([hdc, "list", "targets"]):
            if comm_tools.is_empty(line):
                continue
            line = line.strip()
            if line == "[Empty]":
                continue
            result.append(line)
        return result

    def run_cmd_result_code(self, cmd):
        self.check_connect()
        argv = self._target_argv(cmd)
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
        popen = self.popen(cmd, stdout=subprocess.PIPE)
        try:
            for raw in cmd_runner.iter_stdout_lines(popen.stdout):
                yield comm_tools.get_str(raw)
        finally:
            if popen.stdout:
                popen.stdout.close()
        return_code = popen.wait()
        if return_code:
            raise subprocess.CalledProcessError(return_code, cmd)

    def popen(self, cmd, buf_size=None, stdout=None, stderr=None, universal_newlines=None):
        argv = self._target_argv(cmd)
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

    def run_file_cmd(self, *parts):
        """hdc file recv/send style: hdc [-t id] file recv remote local"""
        self.check_connect()
        argv = self._base_argv()
        if comm_tools.is_not_empty(self._device_id):
            argv.extend(["-t", self._device_id])
        argv.extend(parts)
        if self._open_log:
            print("run {0}".format(" ".join(argv)))
        proc = cmd_runner.popen(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = proc.communicate()
        if proc.returncode:
            raise subprocess.CalledProcessError(proc.returncode, argv, output=err)
        return comm_tools.get_str(out)
