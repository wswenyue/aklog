#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by zhangwanxin on 2018/11/4.
import subprocess

import threading


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
    threading.Thread(target=f, args=args).start()

    # version = sys.version_info[0]
    # if version == 3:
    #     import _thread
    #
    #     _thread.start_new_thread(function, args)
    # elif version == 2:
    #     import thread
    #     thread.start_new(function, args)

#
# def test(name, index):
#     while True:
#         print(index)
#         time.sleep(2)
#
# print("test--begin")
# new_thread(test, ("name-11", 2))
# print("test--end")
