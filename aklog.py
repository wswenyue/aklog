#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by zhangwanxin on 2018/11/4.
import argparse
import subprocess

import color_print
from comm_tools import get_str
from log_info import LogMsgParser

AKLOG_VERSION = "v3.0.0"


def log(log_filter=None, ignore_case=False, filter_exact=False, all_log=False, pn=None):
    cmd = ["adb", "logcat", "-v", "long"]
    pro = subprocess.Popen(cmd, bufsize=1, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    err_code = pro.poll()
    parser = LogMsgParser(log_filter=log_filter, filter_ignorecase=ignore_case,
                          filter_exact=filter_exact, pn=pn, log_all=all_log)
    while err_code is None:
        line = pro.stdout.readline().strip()
        if line:
            try:
                str_line = get_str(line)
                parser.parser(str_line)
            except Exception:
                color_print.red("\n===========parser error===============\n")
            # print (">>>>>" + line)
        err_code = pro.poll()


def args_build():
    argsParser = argparse.ArgumentParser(description="Android developer's Swiss Army Knife for Log")
    # parser.add_argument('-update', '--update', dest='update', help='update ak', action='store_true')
    argsParser.add_argument('-v', '--version', action='version', version=AKLOG_VERSION)
    group = argsParser.add_argument_group()
    group.add_argument("-a", "--all", action="store_true", help="all process log")
    group.add_argument("-i", "--ignorecase", action="store_true", help="filter command  optional arg for ignore case")
    group.add_argument("-e", "--filterexact", action="store_true", help="filter command  optional arg for exact match")
    # group.add_argument('-f', '--filter', dest='filter', help='only filter log tag', type=str, nargs=1)
    argsParser.add_argument('-f', '--filter', dest='filter', help='only filter log tag', type=str, nargs=1)
    argsParser.add_argument('-p', '--package', dest='package', help='filter target package apk logs', type=str, nargs=1)

    args = argsParser.parse_args()

    _pn = None
    _filter = None
    _ignore_case = False
    _filter_exact = False
    _all_log = False

    if args.package:
        _pn = str(args.package[0])

    if args.filter:
        _filter = str(args.filter[0])
        _ignore_case = bool(args.ignorecase)
        _filter_exact = bool(args.filterexact)

    if args.all:
        _all_log = bool(args.all)

    log(_filter, ignore_case=_ignore_case, filter_exact=_filter_exact, all_log=_all_log, pn=_pn)


args_build()

# if __name__ == '__main__':
#     # log(None, pn="bangjob")
#     # log("ZLogDebug")
#     log(None)
