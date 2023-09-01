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
from content_filter_format import LogPackageFilterFormat, PackageFilterType, LogTagFilterFormat, LogMsgFilterFormat, \
    LogLevelFilterFormat
from content_format import JsonValueFormat
from log_info import LogLevelHelper
from log_parser import LogMsgParser
from log_print_ctr import LogPrintCtr
from phone_record_video_tools import RecordHelper
from screen_cap_tools import ScreenCapTools


def _to_str_arr(obj: Any) -> List[str]:
    _targetList = []
    for _target in comm_tools.get_iterable(obj):
        if comm_tools.is_not_empty(_target):
            _targetList.append(comm_tools.get_str(_target))
    return _targetList


class AkLogArgs(object):
    AK_LOG_VERSION = "v5.0.0"
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
    # 默认值
    def_cmd_screen_cap_path = "~/Desktop/AkScreen/"
    def_cmd_record_video_path = "~/Desktop/AkRVideo/"

    def _define_args_package(self, args_parser: argparse.ArgumentParser):
        args_package = args_parser.add_mutually_exclusive_group()
        args_package.add_argument('-pc', '--' + self.dest_package_current_top, dest=self.dest_package_current_top,
                                  help='匹配当前前台Top应用包名的日志。不加任何包名过滤条件时默认是此条件',
                                  action='store_true', default=True)
        args_package.add_argument("-pa", "--" + self.dest_package_all, dest=self.dest_package_all,
                                  help="不过滤，支持显示所有包名日志",
                                  action='store_true', default=False)
        args_package.add_argument('-p', '--' + self.dest_package, dest=self.dest_package,
                                  help='匹配指定包名的日志，不需要填写完整包名，只要能区分即可',
                                  type=str, nargs='+')
        args_package.add_argument('-pn', '--' + self.dest_package_not, dest=self.dest_package_not,
                                  help='排除指定包名的日志，支持数组',
                                  type=str, nargs='+')

    def _parser_args_package(self, args: Dict[str, object]) -> LogPackageFilterFormat:
        # top,all,target,ex
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
            # 有默认值，默认是cur top，正常不会走到该分支
            raise ValueError("package error!!")

    def _define_args_tag(self, args_parser: argparse.ArgumentParser):
        args_tag_not_group = args_parser.add_mutually_exclusive_group()
        args_tag_not_group.add_argument('-tnf', '--' + self.dest_tag_not_fuzzy, dest=self.dest_tag_not_fuzzy,
                                        help='模糊匹配tag并过滤掉不显示, 支持数组 eg: -tnf tag1 tag2',
                                        type=str, nargs='+')
        args_tag_not_group.add_argument('-tn', '--' + self.dest_tag_not, dest=self.dest_tag_not,
                                        help='匹配tag并过滤掉不显示, 支持数组 eg: -tn tag1 tag2',
                                        type=str, nargs='+')
        args_tags = args_parser.add_mutually_exclusive_group()
        args_tags.add_argument('-t', '--' + self.dest_tag, dest=self.dest_tag,
                               help='匹配tag, 支持数组 eg: -t tag1 tag2',
                               type=str, nargs='+')
        args_tags.add_argument('-te', '--' + self.dest_tag_exact, dest=self.dest_tag_exact,
                               help='匹配tag, 精准完全匹配, 支持数组 eg: -te tag1 tag2',
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
            # 未设置，不做过滤
            return LogTagFilterFormat(tag_not=tag_not_array, is_tag_not_fuzzy=is_tag_not_fuzzy)

    def _define_args_msg(self, args_parser: argparse.ArgumentParser):
        args_parser.add_argument('-mn', '--' + self.dest_msg_not, dest=self.dest_msg_not,
                                 help='匹配日志内容关键词并过滤掉不显示，支持数组 eg: -mn msg1 msg2',
                                 type=str, nargs='+')
        args_msg = args_parser.add_mutually_exclusive_group()
        args_msg.add_argument('-m', '--' + self.dest_msg, dest=self.dest_msg,
                              help='匹配日志内容关键词，支持数组 eg: -m msg1 msg2',
                              type=str, nargs='+')
        args_msg.add_argument('-mjson', '--' + self.dest_msg_json_value, dest=self.dest_msg_json_value,
                              help='匹配日志内容中JSON结构的数据，并获取指定key的值。例如 -mjson keyA keyB '
                                   '将匹配带有"keyA"或"keyB"的json数据，并将对应的值解析出来',
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
                raise ValueError("msg filter -mjson empty value!!")
            return LogMsgFilterFormat(
                msg_not=msg_not_array,
                json_format=JsonValueFormat(_keys=_array))
        elif args[self.dest_msg]:
            _array = _to_str_arr(args[self.dest_msg])
            if comm_tools.is_empty(_array):
                raise ValueError("msg filter -m empty value!!")
            return LogMsgFilterFormat(target=_array, msg_not=msg_not_array)
        else:
            # 未设置，不做过滤
            return LogMsgFilterFormat(msg_not=msg_not_array)

    # 日志级别
    def _define_args_level(self, args_parser: argparse.ArgumentParser):
        args_parser.add_argument('-l', '--' + self.dest_level, dest=self.dest_level,
                                 help='匹配日志级别(V|v|2, D|d|3, I|i|4, W|w|5, E|e|6)',
                                 type=str,
                                 nargs=1)

    def _parser_args_level(self, args: Dict[str, object]) -> LogLevelFilterFormat:
        if args[self.dest_level]:
            _level = LogLevelHelper.level_code(comm_tools.get_str(_to_str_arr(args[self.dest_level])[0]))
            if _level == LogLevelHelper.UNKNOWN:
                raise ValueError("level filter value error!!")
            return LogLevelFilterFormat(target=_level)
        else:
            return LogLevelFilterFormat()

    def _define_args_cmd(self, args_parser: argparse.ArgumentParser):
        args_cmd = args_parser.add_mutually_exclusive_group()
        args_cmd.add_argument("-cs", "--" + self.dest_cmd_screen_cap, dest=self.dest_cmd_screen_cap,
                              help=f"命令：获取当前手机截屏，并保持到(传入的)指定位置，默认位置是：${self.def_cmd_screen_cap_path}",
                              type=str, nargs='?', const="null")
        args_cmd.add_argument("-cr", "--" + self.dest_cmd_record_video, dest=self.dest_cmd_record_video,
                              help=f"命令：开始录制当前手机视频，并保持到(传入的)指定位置，默认位置是：${self.def_cmd_record_video_path}",
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
            description=f"Android开发利器-AKLog-{self.AK_LOG_VERSION} (Android developer's Swiss Army Knife for Log)")
        args_parser.add_argument('-v', '--' + self.dest_version, action=self.dest_version, version=self.AK_LOG_VERSION)
        # package 相关参数
        self._define_args_package(args_parser)
        # tag 过滤相关参数
        self._define_args_tag(args_parser)
        # msg 过滤相关参数
        self._define_args_msg(args_parser)
        # 日志级别
        self._define_args_level(args_parser)
        # 命令相关
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
                color_print.red(f"===========parser error===============\n{e}")
                if _line:
                    print(f"==>{_line}<==")
                # print (">>>>>" + line)
            err_code = pro.poll()

    def run(self, argv: Optional[List] = None):
        args_parser = self._define_args()
        args = args_parser.parse_args(args=argv)
        args_var: dict[str, Any] = vars(args)
        if self._parser_run_cmd(args_var):
            return
        self._run_log(args_var)


if __name__ == '__main__':
    # AkLogArgs().run("-l E".split())
    AkLogArgs().run()
    # main_run("-cr".split())
