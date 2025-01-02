#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by wswenyue on 2018/11/4.
import argparse
import subprocess
from typing import Optional, List, Dict, Any

import color_print
import comm_tools
from adb_utils import AdbHelper
from app_info import AppInfoHelper
from comm_tools import get_str
from content_filter_format import LogPackageFilterFormat, PackageFilterType, LogTagFilterFormat, LogMsgFilterFormat, LogLevelFilterFormat
from content_format import JsonValueFormat
from dump_crash_log_tools import DumpCrashLog
from log_info import LogLevelHelper
from log_parser import LogMsgParser
from log_print_ctr import LogPrintCtr
from phone_record_video_tools import RecordHelper, PhoneRecordVideo
from screen_cap_tools import ScreenCapTools

def _to_str_arr(obj: Any) -> List[str]:
    _targetList = []
    for _target in comm_tools.get_iterable(obj):
        if comm_tools.is_not_empty(_target):
            _targetList.append(comm_tools.get_str(_target))
    return _targetList

class AkLogArgs(object):
    AK_LOG_VERSION = "v5.0.5"
    dest_version = "version"
    dest_package = "package"
    dest_package_all = "package_all"
    dest_package_current_top = "package_current_top"
    dest_package_not = "package_not"
    dest_tag = "tag"
    dest_tag_not = "tag_not"
    dest_tag_not_fuzzy = "tag_not_fuzzy"
    dest_tag_case = "tag_case"
    dest_tag_exact = "tag_exact"
    dest_msg = "msg"
    dest_msg_not = "msg_not"
    dest_msg_json_value = "msg_json_value"
    dest_level = "level"
    dest_cmd_screen_cap = "cmd_screen_cap"
    dest_cmd_record_video = "cmd_record_video"
    # Default values
    def_cmd_screen_cap_path = f"~/Desktop/{ScreenCapTools.DEF_PATH_FILE_NAME}/"
    def_cmd_record_video_path = f"~/Desktop/{PhoneRecordVideo.DEF_PATH_FILE_NAME}/"

    def _define_args_package(self, args_parser: argparse.ArgumentParser):
        args_package = args_parser.add_mutually_exclusive_group()
        args_package.add_argument('-pc', '--' + self.dest_package_current_top, dest=self.dest_package_current_top,
                                  help='Match logs from the currently top foreground application. This is the default condition if no package filter is specified.',
                                  action='store_true', default=True)
        args_package.add_argument("-pa", "--" + self.dest_package_all, dest=self.dest_package_all,
                                  help="Show logs from all packages without filtering.",
                                  action='store_true', default=False)
        args_package.add_argument('-p', '--' + self.dest_package, dest=self.dest_package,
                                  help='Match logs from specified package(s). You do not need to provide the full package name; partial names are sufficient.',
                                  type=str, nargs='+')
        args_package.add_argument('-pn', '--' + self.dest_package_not, dest=self.dest_package_not,
                                  help='Exclude logs from specified package(s), supports multiple values.',
                                  type=str, nargs='+')

    def _parser_args_package(self, args: Dict[str, object]) -> LogPackageFilterFormat:
        # top, all, target, exclude
        if args[self.dest_package]:
            return LogPackageFilterFormat(PackageFilterType.TARGET,
                                          _to_str_arr(args[self.dest_package]))
        elif args[self.dest_package_not]:
            return LogPackageFilterFormat(PackageFilterType.EXCLUDE,
                                          _to_str_arr(args[self.dest_package_not]))
        elif args[self.dest_package_all]:
            return LogPackageFilterFormat(PackageFilterType.All)
        elif args[self.dest_package_current_top]:
            return LogPackageFilterFormat(PackageFilterType.Top)
        else:
            # Defaults to current top, should not normally reach this branch.
            raise ValueError("Package filter error!!")

    def _define_args_tag(self, args_parser: argparse.ArgumentParser):
        args_tag_not_group = args_parser.add_mutually_exclusive_group()
        args_tag_not_group.add_argument('-tnf', '--' + self.dest_tag_not_fuzzy, dest=self.dest_tag_not_fuzzy,
                                        help='Fuzzy match tags and filter out logs that do not match. Supports multiple values, e.g., -tnf tag1 tag2.',
                                        type=str, nargs='+')
        args_tag_not_group.add_argument('-tn', '--' + self.dest_tag_not, dest=self.dest_tag_not,
                                        help='Match tags and filter out logs that do not match. Supports multiple values, e.g., -tn tag1 tag2.',
                                        type=str, nargs='+')
        args_tags = args_parser.add_mutually_exclusive_group()
        args_tags.add_argument('-t', '--' + self.dest_tag, dest=self.dest_tag,
                               help='Match specific tags. Supports multiple values, e.g., -t tag1 tag2.',
                               type=str, nargs='+')
        args_tags.add_argument('-te', '--' + self.dest_tag_exact, dest=self.dest_tag_exact,
                               help='Match exact tags. Supports multiple values, e.g., -te tag1 tag2.',
                               type=str, nargs='+')

    def _parser_args_tag(self, args: Dict[str, object]) -> LogTagFilterFormat:
        tag_not_array = None
        is_tag_not_fuzzy = False
        if args[self.dest_tag_not]:
            tag_not_array = _to_str_arr(args[self.dest_tag_not])
            is_tag_not_fuzzy = False
        elif args[self.dest_tag_not_fuzzy]:
            tag_not_array = _to_str_arr(args[self.dest_tag_not_fuzzy])
            is_tag_not_fuzzy = True
        if comm_tools.is_empty(tag_not_array):
            tag_not_array = None
        if args[self.dest_tag]:
            return LogTagFilterFormat(target=_to_str_arr(args[self.dest_tag]), tag_not=tag_not_array,
                                      is_exact=False, is_tag_not_fuzzy=is_tag_not_fuzzy)
        elif args[self.dest_tag_exact]:
            return LogTagFilterFormat(target=_to_str_arr(args[self.dest_tag_exact]), tag_not=tag_not_array,
                                      is_exact=True, is_tag_not_fuzzy=is_tag_not_fuzzy)
        else:
            # Not set, no filtering.
            return LogTagFilterFormat(tag_not=tag_not_array, is_tag_not_fuzzy=is_tag_not_fuzzy)

    def _define_args_msg(self, args_parser: argparse.ArgumentParser):
        args_parser.add_argument('-mn', '--' + self.dest_msg_not, dest=self.dest_msg_not,
                                 help='Match log content keywords and filter out logs that do not match. Supports multiple values, e.g., -mn msg1 msg2.',
                                 type=str, nargs='+')
        args_msg = args_parser.add_mutually_exclusive_group()
        args_msg.add_argument('-m', '--' + self.dest_msg, dest=self.dest_msg,
                              help='Match log content keywords. Supports multiple values, e.g., -m msg1 msg2.',
                              type=str, nargs='+')
        args_msg.add_argument('-mjson', '--' + self.dest_msg_json_value, dest=self.dest_msg_json_value,
                              help='Match JSON data in log content and extract specified key values. For example, -mjson keyA keyB will match logs with "keyA" or "keyB" in JSON data and extract the corresponding values.',
                              type=str, nargs='+')

    def _parser_args_msg(self, args: Dict[str, object]) -> LogMsgFilterFormat:
        msg_not_array = None
        if args[self.dest_msg_not]:
            _array = _to_str_arr(args[self.dest_msg_not])
            if comm_tools.is_not_empty(_array):
                msg_not_array = _array
        if args[self.dest_msg_json_value]:
            _array = _to_str_arr(args[self.dest_msg_json_value])
            if comm_tools.is_empty(_array):
                raise ValueError("Message filter -mjson has empty value!!")
            return LogMsgFilterFormat(
                msg_not=msg_not_array,
                json_format=JsonValueFormat(_keys=_array))
        elif args[self.dest_msg]:
            _array = _to_str_arr(args[self.dest_msg])
            if comm_tools.is_empty(_array):
                raise ValueError("Message filter -m has empty value!!")
            return LogMsgFilterFormat(target=_array, msg_not=msg_not_array)
        else:
            # Not set, no filtering.
            return LogMsgFilterFormat(msg_not=msg_not_array)

    # Log level
    def _define_args_level(self, args_parser: argparse.ArgumentParser):
        args_parser.add_argument('-l', '--' + self.dest_level, dest=self.dest_level,
                                 help='Match log levels (V|v|2, D|d|3, I|i|4, W|w|5, E|e|6).',
                                 type=str,
                                 nargs=1)

    def _parser_args_level(self, args: Dict[str, object]) -> LogLevelFilterFormat:
        if args[self.dest_level]:
            _level = LogLevelHelper.level_code(comm_tools.get_str(_to_str_arr(args[self.dest_level])[0]))
            if _level == LogLevelHelper.UNKNOWN:
                raise ValueError("Log level filter value error!!")
            return LogLevelFilterFormat(target=_level)
        else:
            return LogLevelFilterFormat()

    def _define_args_cmd(self, args_parser: argparse.ArgumentParser):
        args_cmd = args_parser.add_mutually_exclusive_group()
        args_cmd.add_argument("-cs", "--" + self.dest_cmd_screen_cap, dest=self.dest_cmd_screen_cap,
                              help=f"Command: Capture the current phone screen and save it to the specified location (or the default location if none is provided): {self.def_cmd_screen_cap_path}",
                              type=str, nargs='?', const="null")
        args_cmd.add_argument("-cr", "--" + self.dest_cmd_record_video, dest=self.dest_cmd_record_video,
                              help=f"Command: Start recording the current phone screen and save it to the specified location (or the default location if none is provided): {self.def_cmd_record_video_path}",
                              type=str, nargs='?', const="null")

    def _parser_run_cmd(self, args: Dict[str, object]) -> bool:
        # screenCap
        if args[self.dest_cmd_screen_cap]:
            _dir = comm_tools.get_str(args[self.dest_cmd_screen_cap])
            if _dir == 'null':
                _dir = None
            ScreenCapTools(_dir).do_capture()
            return True

        # record video
        if args[self.dest_cmd_record_video]:
            _dir = comm_tools.get_str(args[self.dest_cmd_record_video])
            if _dir == 'null':
                _dir = None
            RecordHelper.do_work(_dir)
            return True

        return False

    def _define_args(self) -> argparse.ArgumentParser:
        args_parser = argparse.ArgumentParser(
            description=f"AKLog - Android Developer's Swiss Army Knife for Log (Version {self.AK_LOG_VERSION})")
        args_parser.add_argument('-v', '--' + self.dest_version, action=self.dest_version, version=self.AK_LOG_VERSION)
        # Package related parameters
        self._define_args_package(args_parser)
        # Tag filtering parameters
        self._define_args_tag(args_parser)
        # Message filtering parameters
        self._define_args_msg(args_parser)
        # Log level
        self._define_args_level(args_parser)
        # Command related
        self._define_args_cmd(args_parser)
        return args_parser

    def _parser_log_args(self, args: Dict[str, object]) -> LogPrintCtr:
        log_printer = LogPrintCtr()
        log_printer.package = self._parser_args_package(args)
        log_printer.tag = self._parser_args_tag(args)
        log_printer.msg = self._parser_args_msg(args)
        log_printer.level = self._parser_args_level(args)
        return log_printer

    def _run_log(self, args_var: Dict[str, object]):
        adb = AdbHelper()
        adb.check_connect()
        AppInfoHelper.start()
        pro = adb.popen("logcat -v long", buf_size=1, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        err_code = pro.poll()
        parser = LogMsgParser(self._parser_log_args(args_var))
        _line = None
        while err_code is None:
            try:
                _line = pro.stdout.readline()
                if _line:
                    str_line = get_str(_line).strip()
                    parser.parser(str_line)
            except Exception as e:
                color_print.red(f"===========Parser Error===============\n{e}")
                if _line:
                    print(f"==>{_line}<==")
                # print (">>>>>" + line)
            err_code = pro.poll()

    def run(self, argv: Optional[List] = None):
        args_parser = self._define_args()
        # args_parser.print_help()
        args = args_parser.parse_args(args=argv)
        args_var: dict[str, Any] = vars(args)
        if self._parser_run_cmd(args_var):
            return
        self._run_log(args_var)


if __name__ == '__main__':
    AkLogArgs().run()