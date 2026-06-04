#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

import sys

if sys.version_info[0] >= 3:
    from abc import ABC, abstractmethod

    class _PlatformBase(ABC):
        pass
else:
    from abc import ABCMeta, abstractmethod

    class _PlatformBase:
        __metaclass__ = ABCMeta


PLATFORM_ANDROID = "android"
PLATFORM_HARMONY = "harmony"


class DeviceInfo:
    def __init__(self, platform, device_id, label):
        self.platform = platform
        self.device_id = device_id
        self.label = label

    def __str__(self):
        return "[{0}] {1} ({2})".format(self.platform, self.label, self.device_id)


class DevicePlatform(_PlatformBase):
    """Unified device operations for Android and HarmonyOS."""

    @property
    @abstractmethod
    def platform(self):
        pass

    @property
    @abstractmethod
    def device_id(self):
        pass

    @classmethod
    @abstractmethod
    def list_devices(cls):
        pass

    @abstractmethod
    def check_connect(self):
        pass

    @abstractmethod
    def run_cmd(self, cmd):
        pass

    @abstractmethod
    def run_cmd_result_code(self, cmd):
        pass

    @abstractmethod
    def cmd_run_iter(self, cmd):
        pass

    @abstractmethod
    def popen(self, cmd, **kwargs):
        pass

    @abstractmethod
    def start_log_stream(self, level=None):
        pass

    @abstractmethod
    def create_log_parser(self, log_printer):
        pass

    @abstractmethod
    def get_foreground_package(self):
        pass

    @abstractmethod
    def iter_processes(self):
        pass

    @abstractmethod
    def capture_screen(self, phone_path, local_path):
        pass

    @abstractmethod
    def start_screen_record(self, phone_filename):
        pass

    @abstractmethod
    def stop_screen_record(self, phone_filename):
        pass

    @abstractmethod
    def pull_file(self, remote, local):
        pass

    @abstractmethod
    def remove_remote_file(self, remote):
        pass

    @abstractmethod
    def install_package(self, local_path):
        pass

    @abstractmethod
    def dump_crash_logs(self, is_native, max_size, save_dir):
        pass

    def phone_tmp_dir(self):
        if self.platform == PLATFORM_HARMONY:
            return "/data/local/tmp/"
        return "/sdcard/"

    def screen_cap_ext(self):
        if self.platform == PLATFORM_HARMONY:
            return ".jpeg"
        return ".png"
