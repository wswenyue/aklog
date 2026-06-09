#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

import os
import subprocess
import time
from io import StringIO

from aklog.core import comm_tools
from aklog.device.adb import AdbCmd, AdbHelper
from aklog.device.platform import PLATFORM_ANDROID, DeviceInfo, DevicePlatform
from aklog.log.info import LogLevelHelper
from aklog.log.parser import LogMsgParser


class AndroidPlatform(DevicePlatform):
    def __init__(self, device_id):
        self._device_id = device_id
        self._helper = AdbHelper(device_id=device_id)

    @property
    def platform(self):
        return PLATFORM_ANDROID

    @property
    def device_id(self):
        return self._device_id

    @classmethod
    def list_devices(cls):
        if not AdbCmd.find_adb():
            return []
        devices = []
        for serial in AdbHelper.list_connected_devices():
            devices.append(DeviceInfo(PLATFORM_ANDROID, serial, serial))
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

    def start_log_stream(self, level=None):
        cmd = "logcat -v long"
        if comm_tools.is_not_empty(level):
            lv = LogLevelHelper.level_name(LogLevelHelper.level_code(comm_tools.get_str(level)))
            if lv != "UnKnown":
                cmd = "logcat -v long *:{0}".format(lv)
        return self._helper.popen(
            cmd,
            buf_size=1,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=False,
        )

    def create_log_parser(self, log_printer):
        return LogMsgParser(log_printer)

    def get_foreground_package(self):
        try:
            out = self._helper.run_cmd('shell sh -c "dumpsys activity top | grep ACTIVITY"')
            parts = out.strip().split()
            if len(parts) >= 3:
                token = parts[-3]
                if "/" in token:
                    return token.split("/")[0]
        except Exception:
            pass
        try:
            for line in self._helper.cmd_run_iter('shell sh -c "dumpsys window windows | grep mFocusedApp"'):
                line = line.strip()
                if line.startswith("mFocusedApp="):
                    parts = line.split()
                    if len(parts) > 4:
                        return parts[4].split("/")[0]
        except Exception:
            pass
        return ""

    def iter_processes(self):
        is_skip_title = True
        for line in self._helper.cmd_run_iter("shell ps"):
            if is_skip_title or comm_tools.is_empty(line):
                is_skip_title = False
                continue
            ls = line.strip().split()
            if len(ls) != 9:
                continue
            user = ls[0]
            pid = ls[1]
            name = ls[-1]
            if not user.startswith("u0_") or "/" in name or "[" in name or "]" in name:
                continue
            yield pid, name

    def capture_screen(self, phone_path, local_path):
        self._helper.run_cmd("shell screencap -p {0}".format(phone_path))
        self._helper.run_cmd("pull {0} {1}".format(phone_path, local_path))
        self._helper.run_cmd("shell rm {0}".format(phone_path))

    def start_screen_record(self, phone_filename):
        phone_path = os.path.join("/sdcard/", phone_filename).replace("\\", "/")
        self._record_phone_path = phone_path
        return self._helper.popen(
            "shell screenrecord {0}".format(phone_path), stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )

    def stop_screen_record(self, phone_filename):
        phone_path = getattr(self, "_record_phone_path", os.path.join("/sdcard/", phone_filename))
        return phone_path

    def pull_file(self, remote, local):
        self._helper.run_cmd("pull {0} {1}".format(remote, local))

    def remove_remote_file(self, remote):
        self._helper.run_cmd("shell rm {0}".format(remote))

    def install_package(self, local_path):
        self._helper.run_cmd("install -r {0}".format(local_path))

    def dump_crash_logs(self, is_native, max_size, save_dir):
        filter_tag = "data_app_native_crash" if is_native else "data_app_crash"
        log_name = ("native_" if is_native else "app_") + time.strftime("%Y%m%d%H%M%S", time.localtime()) + ".log"
        if comm_tools.is_empty(save_dir):
            log_save_path = os.path.join(comm_tools.get_user_desktop_dir("AkCrash/"), log_name)
        else:
            log_save_path = os.path.join(save_dir, log_name)

        time_list = []
        for line in self._helper.cmd_run_iter("shell dumpsys dropbox"):
            if comm_tools.is_empty(line) or filter_tag not in line:
                continue
            time_list.append(line.split(filter_tag, 1)[0].strip())

        if len(time_list) <= 0:
            print("not found any log for {0}".format(filter_tag))
            return

        buf = StringIO()
        tip_begin = "##########begin######total found:{0} ;max:{1}#####################\n".format(
            len(time_list), max_size
        )
        tip_end = "############end######total found:{0} ;max:{1}#####################\n".format(
            len(time_list), max_size
        )
        tip_newline = "\n----------------------------------------------------------------\n"
        buf.write(tip_begin)
        print(tip_begin)
        for index, t in enumerate(reversed(time_list)):
            out = self._helper.run_cmd("shell dumpsys dropbox --print '{0}'".format(t))
            buf.write(out)
            buf.write(tip_newline)
            print(out)
            print(tip_newline)
            if index >= max_size - 1:
                break
        buf.write(tip_end)
        print(tip_end)
        comm_tools.write_to_file_no_error(buf.getvalue(), log_save_path)
