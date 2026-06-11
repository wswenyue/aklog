#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

from aklog.core import comm_tools
from aklog.device.android import AndroidPlatform
from aklog.device.harmony import HarmonyPlatform
from aklog.device.platform import PLATFORM_ANDROID, PLATFORM_HARMONY


def list_all_devices(platform_filter=None):
    devices = []
    try:
        if not platform_filter or platform_filter == PLATFORM_ANDROID:
            devices.extend(AndroidPlatform.list_devices())
    except Exception:
        pass
    try:
        if not platform_filter or platform_filter == PLATFORM_HARMONY:
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


def _select_device_interactive(devices):
    import sys

    if sys.stdin.isatty() and sys.stdout.isatty():
        try:
            import questionary

            labels = [str(d) for d in devices]
            choice = questionary.select("Multiple devices connected, please select:", choices=labels).ask()
            if choice is not None:
                idx = labels.index(choice)
                return devices[idx]
        except Exception:
            pass
    labels = [str(d) for d in devices]
    idx = comm_tools.prompt_choice(labels, "Multiple devices connected, please select:")
    return devices[idx]


def resolve_device(device_id=None, platform_filter=None):
    devices = list_all_devices(platform_filter=platform_filter)
    if len(devices) == 0:
        pref = platform_filter or "any"
        raise ValueError(
            "No device connected for platform={0}. Connect an Android (adb) or HarmonyOS (hdc) device.".format(pref)
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

    info = _select_device_interactive(devices)
    platform = _create_platform(info)
    platform.check_connect()
    return platform
