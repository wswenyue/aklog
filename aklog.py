#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by zhangwanxin on 2018/11/4.
import argparse
import subprocess

from comm_tools import cmd_run_iter, get_str
from log_info import LogMsgParser

AKLOG_VERSION = "v2.1.0"


def cur_package_name():
    for line in cmd_run_iter("adb shell dumpsys activity top"):
        line = line.strip()
        if line.startswith("ACTIVITY"):
            pn = line.split("/")[0].split(" ")[1]
            return pn
    return None


def cur_pid(package_name):
    '''
    匹配指定包对应的pid信息
    :param package_name:
    :return: {'com.wuba.bangjob': '20628', 'com.wuba.bangjob:pushservice': '20546'}
    '''
    pid_map = {}
    for line in cmd_run_iter("adb shell ps"):
        line = line.strip()
        if package_name in line:
            ls = line.split()
            pid_map[ls[-1]] = ls[1]
    return pid_map


def log(log_filter=None, ignore_case=False, filter_exact=False, all_pid=False):
    cmd = ["adb", "logcat", "-v", "long"]
    pro = subprocess.Popen(cmd, bufsize=1, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    err_code = pro.poll()
    pn = cur_package_name()
    if all_pid:
        pids = None
    else:
        pids = cur_pid(pn)
    parser = LogMsgParser(log_filter=log_filter, filter_ignorecase=ignore_case,
                          filter_exact=filter_exact, pn=pn, pids=pids)
    while err_code is None:
        line = pro.stdout.readline().strip()
        if line:
            parser.parser(get_str(line))
            # print (">>>>>" + line)
        err_code = pro.poll()


argsParser = argparse.ArgumentParser(description="Android developer's Swiss Army Knife for Log")
# parser.add_argument('-update', '--update', dest='update', help='update ak', action='store_true')
argsParser.add_argument('-v', '--version', action='version', version=AKLOG_VERSION)
group = argsParser.add_argument_group()
group.add_argument("-a", "--all", action="store_true", help="all process log")
group.add_argument("-i", "--ignorecase", action="store_true", help="filter command  optional arg for ignore case")
group.add_argument("-e", "--filterexact", action="store_true", help="filter command  optional arg for exact match")
group.add_argument('-f', '--filter', dest='filter', help='only filter log tag', type=str, nargs=1)

args = argsParser.parse_args()

if args.filter:
    log(str(args.filter[0]), ignore_case=args.ignorecase, filter_exact=args.filterexact, all_pid=args.all)
else:
    log(None, all_pid=args.all)
