#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

from aklog.core import comm_tools
from aklog.device.android import AndroidPlatform
from aklog.device.harmony import HarmonyPlatform
from aklog.device.platform import PLATFORM_ANDROID, PLATFORM_HARMONY


def list_all_devices():
    devices = []
    try:
        devices.extend(AndroidPlatform.list_devices())
    except Exception:
        pass
    try:
        devices.extend(HarmonyPlatform.list_devices())
    except Exception:
        pass
    return devices


def _create_platform(info):
    if info.platform == PLATFORM_ANDROID:
        return AndroidPlatform.from_device_info(info)
    if info.platform == PLATFORM_HARMONY:
        return HarmonyPlatform.from_device_info(info)
    raise ValueError("unknown platform: {0}".format(info.platform))


def resolve_device(device_id=None):
    devices = list_all_devices()
    if len(devices) == 0:
        raise ValueError(
            "No device connected. Connect an Android (adb) or HarmonyOS (hdc) device, "
            "or check lib/adb and lib/hdc tools."
        )

    if comm_tools.is_not_empty(device_id):
        for info in devices:
            if info.device_id == device_id:
                platform = _create_platform(info)
                platform.check_connect()
                return platform
        raise ValueError(
            'Device "{0}" not found. Available: {1}'.format(device_id, ", ".join([d.device_id for d in devices]))
        )

    if len(devices) == 1:
        platform = _create_platform(devices[0])
        platform.check_connect()
        return platform

    labels = [str(d) for d in devices]
    idx = comm_tools.prompt_choice(labels, "Multiple devices connected, please select:")
    platform = _create_platform(devices[idx])
    platform.check_connect()
    return platform
