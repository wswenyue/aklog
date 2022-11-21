#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by wswenyue on 2018/11/4.
import argparse
import subprocess
from typing import Optional, List

import color_print
import comm_tools
from adb_utils import AdbHelper
from app_info import AppInfoHelper
from comm_tools import get_str
from format_content import JsonValueFormat
from log_filter import LogFilter
from log_parser import LogMsgParser

AK_LOG_VERSION = "v4.0.1"


def log(_filter: LogFilter):
    adb = AdbHelper()
    adb.check_connect()
    AppInfoHelper.start()
    pro = adb.popen("logcat -v long", buf_size=1, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    err_code = pro.poll()
    parser = LogMsgParser(_filter)
    global _line
    while err_code is None:
        try:
            _line = pro.stdout.readline()
            if _line:
                str_line = get_str(_line).strip()
                parser.parser(str_line)
        except Exception as e:
            color_print.red(f"===========parser error===============\n{e}")
            if _line:
                print(f"==>{_line}<==")
            # print (">>>>>" + line)
        err_code = pro.poll()


def main_run(argv: Optional[List] = None):
    args_parser = argparse.ArgumentParser(description="Android developer's Swiss Army Knife for Log")
    args_parser.add_argument('-v', '--version', action='version', version=AK_LOG_VERSION)

    args_parser.add_argument('-t', '--tag', dest='tag', help='Filter logs with tag', type=str, nargs='+')
    args_parser.add_argument('-l', '--level', dest='level', help='Filter logs using log level (V,D,I,W,E)', type=str,
                             nargs=1)

    args_parser.add_argument('-m', '--msg', dest='msg', help='Filter logs with msg', type=str, nargs='+')
    args_parser.add_argument('-mj', '--msg_json_value', dest='msg_json_value',
                             help='Get the value of the given key from the data of the message content json class '
                                  'structure formatted output, support string array',
                             type=str, nargs='+')

    args_parser.add_argument('-p', '--package', dest='package',
                             help='Filter logs with package',
                             type=str, nargs=1)
    args_parser.add_argument('-pe', '--package_exclude', dest='package_exclude',
                             help='Use package name to exclude logs, support string array',
                             type=str, nargs='+')

    group = args_parser.add_argument_group("ext")
    group.add_argument("-i", "--tag_case", dest='tag_case',
                       help="Filter tags using matching case pattern",
                       action='store_true')
    group.add_argument("-e", "--tag_exact", dest='tag_exact',
                       help="Filter tags using full match mode",
                       action='store_true')
    group.add_argument("-a", "--all_package", dest='all_package',
                       help="Do not filter packages",
                       action='store_true')

    # args_parser.print_help()

    args = args_parser.parse_args(args=argv)
    # print(args)

    _package: Optional[str] = None
    _package_exclude: Optional[List[str]] = None
    _is_tag_exact: bool = False
    _is_tag_ignore_case: bool = True
    _priority: Optional[str] = None
    _is_package_all: bool = False

    if args.package:
        _package = comm_tools.get_str(args.package[0])
    if args.package_exclude:
        _package_exclude = args.package_exclude
    if args.all_package:
        _is_package_all = bool(args.all_package)

    if args.tag_case:
        _is_tag_ignore_case = not bool(args.tag_case)
    if args.tag_exact:
        _is_tag_exact = bool(args.tag_exact)
    if args.level:
        _priority = comm_tools.get_str(args.level[0])

    log_filter = LogFilter(
        _package=_package,
        _package_exclude=_package_exclude,
        _is_package_all=_is_package_all,
        _is_tag_exact=_is_tag_exact, _is_tag_ignore_case=_is_tag_ignore_case,
        _priority=_priority
    )

    if args.tag:
        _tags = []
        for _tag in args.tag:
            if comm_tools.is_not_empty(_tag):
                _tags.append(comm_tools.get_str(_tag))
        log_filter.tags = _tags

    if args.msg:
        _msgs = []
        for _msg in args.msg:
            if comm_tools.is_not_empty(_msg):
                _msgs.append(comm_tools.get_str(_msg))
        log_filter.msgs = _msgs

    if args.msg_json_value:
        json_keys = []
        for key in args.msg_json_value:
            if comm_tools.is_not_empty(key):
                json_keys.append(comm_tools.get_str(key))
        if comm_tools.is_not_empty(json_keys):
            log_filter.msg_format = JsonValueFormat(json_keys)

    log(log_filter)


if __name__ == '__main__':
    main_run()
