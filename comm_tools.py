#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by wswenyue on 2018/11/4.
import errno
import os
import platform
import subprocess
import sys

import threading
from typing import Tuple


def is_empty(obj):
    if obj is None:
        return True
    if not obj:
        return True
    if type(obj) is str:
        if obj == "":
            return True
        elif obj.strip() == "":
            return True
    if type(obj) is list:
        if len(obj) <= 0:
            return True
    if type(obj) is dict:
        return bool(obj)
    else:
        return False


def is_not_empty(obj):
    return not is_empty(obj)


def get_str(obj):
    if type(obj) is str:
        return obj
    elif type(obj) is bytes:
        return bytes.decode(obj, encoding="utf-8", errors="ignore")
        # return obj.decode("utf-8")
    else:
        return str(obj)


def cmd_run_iter(cmd):
    _cmd = str(cmd).split()
    popen = subprocess.Popen(_cmd, stdout=subprocess.PIPE, universal_newlines=True)
    for stdout_line in iter(popen.stdout.readline, ""):
        yield get_str(stdout_line)
    popen.stdout.close()
    return_code = popen.wait()
    if return_code:
        raise subprocess.CalledProcessError(return_code, _cmd)


def cmd_run(cmd):
    _cmd = str(cmd).split()
    output = subprocess.check_output(_cmd)
    return get_str(output)


def new_thread(f, name: str = None, args: Tuple = ()):
    t = threading.Thread(target=f, args=args)
    t.setDaemon(True)
    if name:
        t.name = name
    t.start()


def is_py3():
    return sys.version_info[0] == 3


def is_windows_os() -> bool:
    # The output of platform.system() is as follows:
    # Linux: Linux
    # Mac: Darwin
    # Windows: Windows
    return platform.system() == "Windows"


def is_mac_os() -> bool:
    # The output of platform.system() is as follows:
    # Linux: Linux
    # Mac: Darwin
    # Windows: Windows
    return platform.system() == "Darwin"


def get_user_home_dir() -> str:
    if is_windows_os():
        return os.path.join(os.environ['USERPROFILE'])
    else:
        return os.path.join(os.path.expanduser('~'))


def get_user_desktop_dir(file_name: str = None) -> str:
    if file_name:
        return os.path.join(os.path.join(get_user_home_dir(), 'Desktop'), file_name)
    else:
        return os.path.join(get_user_home_dir(), 'Desktop')


def create_dir_not_exists(path):
    if os.path.exists(path) and os.path.isdir(path):
        # print(f"{path} already exists!!!")
        return
    try:
        dir_path = os.path.dirname(path)
        os.makedirs(dir_path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise exception


def is_exe(fpath: str) -> bool:
    """
    check file path is executable file
    :param fpath:
    :return:
    """
    if not fpath:
        return False
    return os.path.isfile(fpath) and os.access(fpath, os.X_OK)


def match_str(a: str, b: str, is_exact: bool = True, is_ignore_case: bool = False) -> bool:
    """
    a str match b str
    :param a:
    :param b:
    :param is_exact: 精准匹配
    :param is_ignore_case: 忽略大小写
    :return: true:matched
    """
    if is_empty(a) or is_empty(b):
        return False
    if is_exact:
        if is_ignore_case:
            return a.lower() == b.lower()
        else:
            return a == b
    else:
        if is_ignore_case:
            return a.lower() in b.lower()
        else:
            return a in b
