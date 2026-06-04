#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

import os
import platform

from aklog.core import comm_tools

_PKG_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def package_dir():
    return _PKG_DIR


def project_root():
    return os.path.dirname(os.path.dirname(_PKG_DIR))


def lib_dir():
    return os.path.join(project_root(), "lib")


def host_os():
    if comm_tools.is_windows_os():
        return "windows"
    if comm_tools.is_mac_os():
        return "darwin"
    return "linux"


def host_arch():
    machine = platform.machine().lower()
    if machine in ("arm64", "aarch64"):
        return "aarch64" if host_os() == "linux" else "arm64"
    if machine in ("x86_64", "amd64"):
        return "x86_64"
    if machine in ("i386", "i686"):
        return "x86_64"
    return machine


def bundled_lib_dir():
    return os.path.join(lib_dir(), host_os(), host_arch())


def bundled_tool(name):
    arch_path = os.path.join(bundled_lib_dir(), name)
    if os.path.exists(arch_path):
        return arch_path
    legacy_path = os.path.join(lib_dir(), name)
    if os.path.exists(legacy_path):
        return legacy_path
    return arch_path
