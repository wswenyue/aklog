#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by zhangwanxin on 2018/11/4.
import subprocess

import threading

import sys


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
    else:
        return False


def is_not_empty(obj):
    return not is_empty(obj)


def get_str(obj):
    if type(obj) is str:
        return obj
    elif type(obj) is bytes:
        return obj.decode("utf-8")
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


def new_thread(f, args):
    t = threading.Thread(target=f, args=args)
    t.setDaemon(True)
    t.start()


def is_py3():
    return sys.version_info[0] == 3

