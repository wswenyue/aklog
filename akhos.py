#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by wswenyue on 2018/11/4.
import argparse
import os
from typing import Optional, List, Dict, Any

import yaml

import comm_tools
from hdc_cmd import HdcCmd
from screen_cap_tools import ScreenCapTools


def _to_str_arr(obj: Any) -> List[str]:
    _targetList = []
    for _target in comm_tools.get_iterable(obj):
        if comm_tools.is_not_empty(_target):
            _targetList.append(comm_tools.get_str(_target))
    return _targetList


class AkHosArgs(object):
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
    dest_cmd = "cmd"
    # 默认值
    cmd_name_define: Dict[str, List[str]] = {}

    def __init__(self):
        cur_path = os.path.dirname(os.path.realpath(__file__))
        cfg_path = os.path.join(cur_path, "cfg.yml")
        with open(cfg_path, 'r') as f:
            self.cfg = yaml.load(f, Loader=yaml.SafeLoader)
        version = self.cfg['version']
        self.AK_HOS_VERSION = f"{version['prefix']}{version['major']}.{version['minor']}.x"

    # def _define_args_package(self, args_parser: argparse.ArgumentParser):
    #     args_package = args_parser.add_mutually_exclusive_group()
    #     args_package.add_argument('-pc', '--' + self.dest_package_current_top, dest=self.dest_package_current_top,
    #                               help='匹配当前前台Top应用包名的日志。不加任何包名过滤条件时默认是此条件',
    #                               action='store_true', default=True)
    #     args_package.add_argument("-pa", "--" + self.dest_package_all, dest=self.dest_package_all,
    #                               help="不过滤，支持显示所有包名日志",
    #                               action='store_true', default=False)
    #     args_package.add_argument('-p', '--' + self.dest_package, dest=self.dest_package,
    #                               help='匹配指定包名的日志，不需要填写完整包名，只要能区分即可',
    #                               type=str, nargs='+')
    #     args_package.add_argument('-pn', '--' + self.dest_package_not, dest=self.dest_package_not,
    #                               help='排除指定包名的日志，支持数组',
    #                               type=str, nargs='+')
    #
    # def _parser_args_package(self, args: Dict[str, object]) -> LogPackageFilterFormat:
    #     # top,all,target,ex
    #     if args[self.dest_package]:
    #         return LogPackageFilterFormat(PackageFilterType.TARGET,
    #                                       _to_str_arr(args[self.dest_package]))
    #     elif args[self.dest_package_not]:
    #         return LogPackageFilterFormat(PackageFilterType.EXCLUDE,
    #                                       _to_str_arr(args[self.dest_package_not]))
    #     elif args[self.dest_package_all]:
    #         return LogPackageFilterFormat(PackageFilterType.All)
    #     elif args[self.dest_package_current_top]:
    #         return LogPackageFilterFormat(PackageFilterType.Top)
    #     else:
    #         # 有默认值，默认是cur top，正常不会走到该分支
    #         raise ValueError("package error!!")
    #
    # def _define_args_tag(self, args_parser: argparse.ArgumentParser):
    #     args_tag_not_group = args_parser.add_mutually_exclusive_group()
    #     args_tag_not_group.add_argument('-tnf', '--' + self.dest_tag_not_fuzzy, dest=self.dest_tag_not_fuzzy,
    #                                     help='模糊匹配tag并过滤掉不显示, 支持数组 eg: -tnf tag1 tag2',
    #                                     type=str, nargs='+')
    #     args_tag_not_group.add_argument('-tn', '--' + self.dest_tag_not, dest=self.dest_tag_not,
    #                                     help='匹配tag并过滤掉不显示, 支持数组 eg: -tn tag1 tag2',
    #                                     type=str, nargs='+')
    #     args_tags = args_parser.add_mutually_exclusive_group()
    #     args_tags.add_argument('-t', '--' + self.dest_tag, dest=self.dest_tag,
    #                            help='匹配tag, 支持数组 eg: -t tag1 tag2',
    #                            type=str, nargs='+')
    #     args_tags.add_argument('-te', '--' + self.dest_tag_exact, dest=self.dest_tag_exact,
    #                            help='匹配tag, 精准完全匹配, 支持数组 eg: -te tag1 tag2',
    #                            type=str, nargs='+')
    #
    # def _parser_args_tag(self, args: Dict[str, object]) -> LogTagFilterFormat:
    #     tag_not_array = None
    #     is_tag_not_fuzzy = False
    #     if args[self.dest_tag_not]:
    #         tag_not_array = _to_str_arr(args[self.dest_tag_not])
    #         is_tag_not_fuzzy = False
    #     elif args[self.dest_tag_not_fuzzy]:
    #         tag_not_array = _to_str_arr(args[self.dest_tag_not_fuzzy])
    #         is_tag_not_fuzzy = True
    #     if comm_tools.is_empty(tag_not_array):
    #         tag_not_array = None
    #     if args[self.dest_tag]:
    #         return LogTagFilterFormat(target=_to_str_arr(args[self.dest_tag]), tag_not=tag_not_array,
    #                                   is_exact=False, is_tag_not_fuzzy=is_tag_not_fuzzy)
    #     elif args[self.dest_tag_exact]:
    #         return LogTagFilterFormat(target=_to_str_arr(args[self.dest_tag_exact]), tag_not=tag_not_array,
    #                                   is_exact=True, is_tag_not_fuzzy=is_tag_not_fuzzy)
    #     else:
    #         # 未设置，不做过滤
    #         return LogTagFilterFormat(tag_not=tag_not_array, is_tag_not_fuzzy=is_tag_not_fuzzy)
    #
    # def _define_args_msg(self, args_parser: argparse.ArgumentParser):
    #     args_parser.add_argument('-mn', '--' + self.dest_msg_not, dest=self.dest_msg_not,
    #                              help='匹配日志内容关键词并过滤掉不显示，支持数组 eg: -mn msg1 msg2',
    #                              type=str, nargs='+')
    #     args_msg = args_parser.add_mutually_exclusive_group()
    #     args_msg.add_argument('-m', '--' + self.dest_msg, dest=self.dest_msg,
    #                           help='匹配日志内容关键词，支持数组 eg: -m msg1 msg2',
    #                           type=str, nargs='+')
    #     args_msg.add_argument('-mjson', '--' + self.dest_msg_json_value, dest=self.dest_msg_json_value,
    #                           help='匹配日志内容中JSON结构的数据，并获取指定key的值。例如 -mjson keyA keyB '
    #                                '将匹配带有"keyA"或"keyB"的json数据，并将对应的值解析出来',
    #                           type=str, nargs='+')
    #
    # def _parser_args_msg(self, args: Dict[str, object]) -> LogMsgFilterFormat:
    #     msg_not_array = None
    #     if args[self.dest_msg_not]:
    #         _array = _to_str_arr(args[self.dest_msg_not])
    #         if comm_tools.is_not_empty(_array):
    #             msg_not_array = _array
    #     if args[self.dest_msg_json_value]:
    #         _array = _to_str_arr(args[self.dest_msg_json_value])
    #         if comm_tools.is_empty(_array):
    #             raise ValueError("msg filter -mjson empty value!!")
    #         return LogMsgFilterFormat(
    #             msg_not=msg_not_array,
    #             json_format=JsonValueFormat(_keys=_array))
    #     elif args[self.dest_msg]:
    #         _array = _to_str_arr(args[self.dest_msg])
    #         if comm_tools.is_empty(_array):
    #             raise ValueError("msg filter -m empty value!!")
    #         return LogMsgFilterFormat(target=_array, msg_not=msg_not_array)
    #     else:
    #         # 未设置，不做过滤
    #         return LogMsgFilterFormat(msg_not=msg_not_array)
    #
    # # 日志级别
    # def _define_args_level(self, args_parser: argparse.ArgumentParser):
    #     args_parser.add_argument('-l', '--' + self.dest_level, dest=self.dest_level,
    #                              help='匹配日志级别(V|v|2, D|d|3, I|i|4, W|w|5, E|e|6)',
    #                              type=str,
    #                              nargs=1)
    #
    # def _parser_args_level(self, args: Dict[str, object]) -> LogLevelFilterFormat:
    #     if args[self.dest_level]:
    #         _level = LogLevelHelper.level_code(comm_tools.get_str(_to_str_arr(args[self.dest_level])[0]))
    #         if _level == LogLevelHelper.UNKNOWN:
    #             raise ValueError("level filter value error!!")
    #         return LogLevelFilterFormat(target=_level)
    #     else:
    #         return LogLevelFilterFormat()

    def _define_args_cmd(self, args_parser: argparse.ArgumentParser):
        comm_cmd = args_parser.add_subparsers(dest=self.dest_cmd, title="常用命令", description="快捷执行常用的命令",
                                              help="常用命令使用说明")

        install = comm_cmd.add_parser('install', aliases=['i'], help="install hap")
        self.cmd_name_define['install'] = ['install', 'i']
        install.add_argument('-path', type=str,
                             help=f"命令：安装hap包")

        cap = comm_cmd.add_parser('cap-screen', aliases=['cs'], help="获取当前手机截屏")
        self.cmd_name_define['cap-screen'] = ['cap-screen', 'cs']
        cap.add_argument('-path', type=str,
                         help=f"命令：获取当前手机截屏，并保持到(传入的)指定位置，默认位置是：${ScreenCapTools.def_screen_cap_path}")
        #
        # record = comm_cmd.add_parser('record-video', aliases=['rv'], help="录制当前手机屏幕")
        # self.cmd_name_define['record-video'] = ['record-video', 'rv']
        # record.add_argument('-path', type=str,
        #                     help=f"命令：录制当前手机视频，并保存到(传入的)指定位置。默认位置是：${PhoneRecordVideo.def_record_video_path}")
        #
        # dump = comm_cmd.add_parser('dump-log', aliases=['dump'], help="dump app(或native) 崩溃日志")
        # self.cmd_name_define['dump-log'] = ['dump-log', 'dump']
        # dump.add_argument('-type', type=int, default=0, help="打印日志类型[0:app日志；1:native日志]，默认是打印app日志")
        # dump.add_argument('-maxsize', type=int, default=10, help="最多打印的日志数量")
        # dump.add_argument('-path', type=str,
        #                   help=f"dump app 崩溃日志，并保持到(传入的)指定位置，默认位置是：${DumpCrashLog.DEF_PATH}")

    def _parser_run_cmd(self, args: Dict[str, object]) -> bool:
        cmd = args[self.dest_cmd]
        if comm_tools.is_empty(cmd):
            return False
        if cmd in self.cmd_name_define['cap-screen']:
            _dir = comm_tools.get_str(args['path'])
            if _dir == 'null':
                _dir = None
            ScreenCapTools(_dir, is_harmonyos=True).do_capture()
            return True
        if cmd in self.cmd_name_define['install']:
            HdcCmd().run_cmd(f"install -r {comm_tools.get_str(args['path'])}")
            return True
        # if cmd in self.cmd_name_define['record-video']:
        #     _dir = comm_tools.get_str(args['path'])
        #     if _dir == 'null':
        #         _dir = None
        #     RecordHelper.do_work(_dir)
        #     return True
        # if cmd in self.cmd_name_define['dump-log']:
        #     _dir = comm_tools.get_str(args['path'])
        #     if _dir == 'null':
        #         _dir = None
        #     _type = comm_tools.to_int(args['type'])
        #     _maxsize = comm_tools.to_int(args['maxsize'])
        #     DumpCrashLog(is_ndk=_type != 0, dir=_dir, max_size=_maxsize).do_work()
        #     return True

        print(f"exe failure==>{cmd}")
        return True

    def _define_args(self) -> argparse.ArgumentParser:
        args_parser = argparse.ArgumentParser(
            description=f"Harmony开发利器-akHOS-{self.AK_HOS_VERSION} (Harmony developer's Swiss Army Knife for Log)")
        args_parser.add_argument('-v', '--' + self.dest_version, action=self.dest_version, version=self.AK_HOS_VERSION)
        # package 相关参数
        # self._define_args_package(args_parser)
        # # tag 过滤相关参数
        # self._define_args_tag(args_parser)
        # # msg 过滤相关参数
        # self._define_args_msg(args_parser)
        # # 日志级别
        # self._define_args_level(args_parser)
        # 命令相关
        self._define_args_cmd(args_parser)
        return args_parser

    # def _parser_log_args(self, args: Dict[str, object]) -> LogPrintCtr:
    #     log_printer = LogPrintCtr()
    #     log_printer.package = self._parser_args_package(args)
    #     log_printer.tag = self._parser_args_tag(args)
    #     log_printer.msg = self._parser_args_msg(args)
    #     log_printer.level = self._parser_args_level(args)
    #     return log_printer

    # def _run_log(self, args_var: Dict[str, object]):
    #     adb = AdbHelper()
    #     adb.check_connect()
    #     AppInfoHelper.start()
    #     pro = adb.popen("logcat -v long", buf_size=1, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    #     err_code = pro.poll()
    #     parser = LogMsgParser(self._parser_log_args(args_var))
    #     _line = None
    #     while err_code is None:
    #         try:
    #             _line = pro.stdout.readline()
    #             if _line:
    #                 str_line = get_str(_line).strip()
    #                 parser.parser(str_line)
    #         except Exception as e:
    #             color_print.red(f"===========parser error===============\n{e}")
    #             if _line:
    #                 print(f"==>{_line}<==")
    #             # print (">>>>>" + line)
    #         err_code = pro.poll()

    def run(self, argv: Optional[List] = None):
        args_parser = self._define_args()
        # args_parser.print_help()
        args = args_parser.parse_args(args=argv)
        args_var: Dict[str, Any] = vars(args)
        if self._parser_run_cmd(args_var):
            return
        # self._run_log(args_var)


if __name__ == '__main__':
    AkHosArgs().run()
