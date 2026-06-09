#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

import os
import re
import subprocess
import time

from aklog.core import comm_tools
from aklog.device.hdc import HdcCmd, HdcHelper
from aklog.device.platform import PLATFORM_HARMONY, DeviceInfo, DevicePlatform
from aklog.log.info import LogLevelHelper
from aklog.log.parser import HilogMsgParser

_SCREEN_RECORDER = "com.huawei.hmos.screenrecorder"
_SCREEN_ABILITY = "com.huawei.hmos.screenrecorder.ServiceExtAbility"
_FAULT_LOG_DIR = "/data/log/faultlog/faultlogger/"


class HarmonyPlatform(DevicePlatform):
    def __init__(self, device_id):
        self._device_id = device_id
        self._helper = HdcHelper(device_id=device_id)

    @property
    def platform(self):
        return PLATFORM_HARMONY

    @property
    def device_id(self):
        return self._device_id

    @classmethod
    def list_devices(cls):
        if not HdcCmd.find_hdc():
            return []
        devices = []
        for target in HdcHelper.list_connected_devices():
            devices.append(DeviceInfo(PLATFORM_HARMONY, target, target))
        return devices

    @classmethod
    def from_device_info(cls, info):
        return cls(info.device_id)

    def check_connect(self):
        self._helper.check_connect()

    def run_cmd(self, cmd):
        return self._helper.run_cmd(cmd)

    def run_cmd_result_code(self, cmd):
        return self._helper.run_cmd_result_code(cmd)

    def cmd_run_iter(self, cmd):
        return self._helper.cmd_run_iter(cmd)

    def popen(self, cmd, **kwargs):
        return self._helper.popen(cmd, **kwargs)

    def _hilog_level_flag(self, level):
        if comm_tools.is_empty(level):
            return ""
        code = LogLevelHelper.level_code(comm_tools.get_str(level))
        name = LogLevelHelper.level_name(code)
        if name == "UnKnown":
            return ""
        if name == "V":
            return "V"
        return name

    def start_log_stream(self, level=None):
        lv = self._hilog_level_flag(level)
        if comm_tools.is_not_empty(lv):
            cmd = "shell hilog -L {0}".format(lv)
        else:
            cmd = "shell hilog"
        return self._helper.popen(
            cmd,
            buf_size=1,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=False,
        )

    def create_log_parser(self, log_printer):
        return HilogMsgParser(log_printer)

    def get_foreground_package(self):
        try:
            out = self._helper.run_cmd("shell aa dump -l")
        except Exception:
            return ""
        blocks = out.split("Mission ID")
        for block in blocks:
            if "FOREGROUND" not in block:
                continue
            match = re.search(r"bundle name \[([^\]]+)\]", block)
            if match:
                return match.group(1).strip()
            match = re.search(r"app name \[([^\]]+)\]", block)
            if match:
                return match.group(1).strip()
        return ""

    @staticmethod
    def _looks_like_bundle_name(name):
        if comm_tools.is_empty(name) or "/" in name or name.startswith("["):
            return False
        base = name.split(":", 1)[0]
        if "." not in base:
            return False
        for suffix in (".elf", ".ko", ".so"):
            if base.endswith(suffix):
                return False
        return True

    def iter_processes(self):
        try:
            out = self._helper.run_cmd("shell ps -ef")
        except Exception:
            return
        is_skip = True
        for line in out.splitlines():
            if is_skip or comm_tools.is_empty(line):
                is_skip = False
                continue
            ls = line.strip().split()
            # Harmony ps -ef: UID PID PPID C STIME TTY TIME CMD
            if len(ls) < 8:
                continue
            pid = ls[1]
            name = ls[7]
            if not self._looks_like_bundle_name(name):
                continue
            yield pid, name

    def capture_screen(self, phone_path, local_path):
        self._helper.run_cmd("shell snapshot_display -f {0}".format(phone_path))
        self._helper.run_file_cmd("file", "recv", phone_path, local_path)
        self._helper.run_cmd("shell rm {0}".format(phone_path))

    def start_screen_record(self, phone_filename):
        self._record_name = phone_filename
        self._helper.run_cmd(
            'shell aa start -b {0} -a {1} --ps "CustomizedFileName" "{2}"'.format(
                _SCREEN_RECORDER, _SCREEN_ABILITY, phone_filename
            )
        )

    def stop_screen_record(self, phone_filename):
        self._helper.run_cmd("shell aa start -b {0} -a {1}".format(_SCREEN_RECORDER, _SCREEN_ABILITY))
        name = getattr(self, "_record_name", phone_filename)
        try:
            out = self._helper.run_cmd("shell mediatool query {0} -u".format(name))
            path = out.strip().splitlines()[-1].strip()
            if comm_tools.is_not_empty(path):
                return path
        except Exception:
            pass
        return name

    def pull_file(self, remote, local):
        self._helper.run_file_cmd("file", "recv", remote, local)

    def remove_remote_file(self, remote):
        self._helper.run_cmd("shell rm {0}".format(remote))

    def install_package(self, local_path):
        self._helper.run_cmd("install -r {0}".format(local_path))

    def dump_crash_logs(self, is_native, max_size, save_dir):
        prefix = "cppcrash" if is_native else "appcrash"
        log_name = ("native_" if is_native else "app_") + time.strftime("%Y%m%d%H%M%S", time.localtime()) + ".log"
        if comm_tools.is_empty(save_dir):
            local_dir = comm_tools.get_user_desktop_dir("AkCrash/")
        else:
            local_dir = save_dir
        comm_tools.create_dir_not_exists(os.path.join(local_dir, log_name))

        listing = self._helper.run_cmd("shell ls {0}".format(_FAULT_LOG_DIR))
        files = []
        for line in listing.splitlines():
            name = line.strip()
            if name.startswith(prefix):
                files.append(name)
        files.sort()
        if len(files) <= 0:
            print("not found any log for {0} in {1}".format(prefix, _FAULT_LOG_DIR))
            return

        selected = files[-max_size:]
        buf_lines = []
        for name in reversed(selected):
            remote = _FAULT_LOG_DIR + name
            local_path = os.path.join(local_dir, name)
            try:
                self.pull_file(remote, local_path)
                with open(local_path, encoding=comm_tools.TEXT_ENCODING, errors="replace") as fp:
                    buf_lines.append(fp.read())
            except Exception as e:
                print("pull {0} failed: {1}".format(name, e))

        log_save_path = os.path.join(local_dir, log_name)
        comm_tools.write_to_file_no_error("\n".join(buf_lines), log_save_path)
        print("saved to {0}".format(log_save_path))
