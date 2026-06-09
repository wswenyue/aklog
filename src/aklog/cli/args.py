#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

import argparse

from aklog.build_meta import GIT_TAG
from aklog.core import comm_tools
from aklog.core.config import load_config
from aklog.log.filter import (
    FilterChain,
    LevelFilter,
    MsgProcessor,
    PackageFilter,
    PackageMode,
    TagFilter,
)
from aklog.log.format import JsonValueFormat
from aklog.log.info import LogLevelHelper
from aklog.log.printer import LogPrintCtr
from aklog.log.theme import LogColorTheme
from aklog.tools.dump_crash import DumpCrashLog
from aklog.tools.record_video import RecordHelper
from aklog.tools.screen_cap import ScreenCapTools


def _to_str_arr(obj):
    result = []
    for _target in comm_tools.get_iterable(obj):
        if comm_tools.is_not_empty(_target):
            result.append(comm_tools.get_str(_target))
    return result


class ChineseArgumentParser(argparse.ArgumentParser):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("add_help", False)
        super().__init__(*args, **kwargs)
        self._optionals.title = "可选参数"
        self._positionals.title = "位置参数"
        self.add_argument(
            "-h",
            "--help",
            action="help",
            default=argparse.SUPPRESS,
            help="显示帮助信息并退出",
        )


class AkLogCli:
    dest_version = "version"
    dest_device = "device"
    dest_package = "package"
    dest_package_all = "package_all"
    dest_package_current_top = "package_current_top"
    dest_package_not = "package_not"
    dest_tag = "tag"
    dest_tag_not = "tag_not"
    dest_tag_not_exact = "tag_not_exact"
    dest_tag_exact = "tag_exact"
    dest_msg = "msg"
    dest_msg_not = "msg_not"
    dest_msg_not_exact = "msg_not_exact"
    dest_msg_exact = "msg_exact"
    dest_msg_json_value = "msg_json_value"
    dest_level = "level"
    dest_cmd = "cmd"
    cmd_name_define = {}

    def __init__(self):
        self.AK_LOG_VERSION = GIT_TAG

    def _define_args_package(self, args_parser):
        args_package = args_parser.add_mutually_exclusive_group()
        args_package.add_argument(
            "-pc",
            "--" + self.dest_package_current_top,
            dest=self.dest_package_current_top,
            help="匹配当前前台应用日志（未指定包名过滤时默认）",
            action="store_true",
        )
        args_package.add_argument(
            "-pa",
            "--" + self.dest_package_all,
            dest=self.dest_package_all,
            help="显示所有应用的日志",
            action="store_true",
        )
        args_package.add_argument(
            "-p",
            "--" + self.dest_package,
            dest=self.dest_package,
            help="匹配指定包名（可多个）",
            type=str,
            nargs="+",
        )
        args_package.add_argument(
            "-pn",
            "--" + self.dest_package_not,
            dest=self.dest_package_not,
            help="排除包含指定包名的日志（模糊匹配）",
            type=str,
            nargs="+",
        )

    def _apply_package_default(self, args):
        if args[self.dest_package] or args[self.dest_package_not] or args[self.dest_package_all]:
            return
        args[self.dest_package_current_top] = True

    def _build_package_filter(self, args):
        if args[self.dest_package]:
            return PackageFilter(PackageMode.TARGET, _to_str_arr(args[self.dest_package]))
        if args[self.dest_package_not]:
            return PackageFilter(PackageMode.EXCLUDE, _to_str_arr(args[self.dest_package_not]))
        if args[self.dest_package_all]:
            return PackageFilter(PackageMode.ALL)
        if args[self.dest_package_current_top]:
            return PackageFilter(PackageMode.TOP)
        return PackageFilter(PackageMode.TOP)

    def _define_args_tag(self, args_parser):
        args_parser.add_argument(
            "-tn",
            "--" + self.dest_tag_not,
            dest=self.dest_tag_not,
            help="排除包含指定 tag 的日志（忽略大小写模糊匹配，规则同 -t）",
            type=str,
            nargs="+",
        )
        args_parser.add_argument(
            "-ten",
            "--" + self.dest_tag_not_exact,
            dest=self.dest_tag_not_exact,
            help="排除精确匹配的 tag（规则同 -te）",
            type=str,
            nargs="+",
        )
        args_tags = args_parser.add_mutually_exclusive_group()
        args_tags.add_argument(
            "-t",
            "--" + self.dest_tag,
            dest=self.dest_tag,
            help="匹配 tag（忽略大小写模糊匹配，包含即接受）",
            type=str,
            nargs="+",
        )
        args_tags.add_argument(
            "-te",
            "--" + self.dest_tag_exact,
            dest=self.dest_tag_exact,
            help="精确匹配 tag",
            type=str,
            nargs="+",
        )

    def _build_tag_filter(self, args):
        exclude_fuzzy = None
        exclude_exact = None
        if args[self.dest_tag_not]:
            exclude_fuzzy = _to_str_arr(args[self.dest_tag_not]) or None
        if args[self.dest_tag_not_exact]:
            exclude_exact = _to_str_arr(args[self.dest_tag_not_exact]) or None
        if comm_tools.is_empty(exclude_fuzzy):
            exclude_fuzzy = None
        if comm_tools.is_empty(exclude_exact):
            exclude_exact = None
        if args[self.dest_tag]:
            return TagFilter(
                include=_to_str_arr(args[self.dest_tag]),
                exact=False,
                exclude_fuzzy=exclude_fuzzy,
                exclude_exact=exclude_exact,
            )
        if args[self.dest_tag_exact]:
            return TagFilter(
                include=_to_str_arr(args[self.dest_tag_exact]),
                exact=True,
                exclude_fuzzy=exclude_fuzzy,
                exclude_exact=exclude_exact,
            )
        return TagFilter(exclude_fuzzy=exclude_fuzzy, exclude_exact=exclude_exact)

    def _define_args_msg(self, args_parser):
        args_parser.add_argument(
            "-mn",
            "--" + self.dest_msg_not,
            dest=self.dest_msg_not,
            help="排除包含指定关键词的消息（忽略大小写模糊匹配，规则同 -m）",
            type=str,
            nargs="+",
        )
        args_parser.add_argument(
            "-men",
            "--" + self.dest_msg_not_exact,
            dest=self.dest_msg_not_exact,
            help="排除精确匹配的消息（规则同 -me）",
            type=str,
            nargs="+",
        )
        args_msg = args_parser.add_mutually_exclusive_group()
        args_msg.add_argument(
            "-m",
            "--" + self.dest_msg,
            dest=self.dest_msg,
            help="匹配消息关键词（忽略大小写模糊匹配，包含即接受）",
            type=str,
            nargs="+",
        )
        args_msg.add_argument(
            "-me",
            "--" + self.dest_msg_exact,
            dest=self.dest_msg_exact,
            help="精确匹配消息",
            type=str,
            nargs="+",
        )
        args_msg.add_argument(
            "-mjson",
            "--" + self.dest_msg_json_value,
            dest=self.dest_msg_json_value,
            help="匹配日志消息中的 JSON 键",
            type=str,
            nargs="+",
        )

    def _build_msg_processor(self, args):
        exclude_fuzzy = None
        exclude_exact = None
        if args[self.dest_msg_not]:
            exclude_fuzzy = _to_str_arr(args[self.dest_msg_not]) or None
        if args[self.dest_msg_not_exact]:
            exclude_exact = _to_str_arr(args[self.dest_msg_not_exact]) or None
        if comm_tools.is_empty(exclude_fuzzy):
            exclude_fuzzy = None
        if comm_tools.is_empty(exclude_exact):
            exclude_exact = None
        common = {"exclude_fuzzy": exclude_fuzzy, "exclude_exact": exclude_exact}
        if args[self.dest_msg_json_value]:
            _array = _to_str_arr(args[self.dest_msg_json_value])
            if comm_tools.is_empty(_array):
                raise ValueError("msg filter -mjson empty value!!")
            return MsgProcessor(json_format=JsonValueFormat(_keys=_array), **common)
        if args[self.dest_msg]:
            _array = _to_str_arr(args[self.dest_msg])
            if comm_tools.is_empty(_array):
                raise ValueError("msg filter -m empty value!!")
            return MsgProcessor(include=_array, exact=False, **common)
        if args[self.dest_msg_exact]:
            _array = _to_str_arr(args[self.dest_msg_exact])
            if comm_tools.is_empty(_array):
                raise ValueError("msg filter -me empty value!!")
            return MsgProcessor(include=_array, exact=True, **common)
        return MsgProcessor(**common)

    def _define_args_level(self, args_parser):
        args_parser.add_argument(
            "-l", "--" + self.dest_level, dest=self.dest_level, help="日志级别 V|D|I|W|E 或 2-6", type=str, nargs=1
        )

    def _build_level_filter(self, args):
        if args[self.dest_level]:
            _level = LogLevelHelper.level_code(comm_tools.get_str(_to_str_arr(args[self.dest_level])[0]))
            if _level == LogLevelHelper.UNKNOWN:
                raise ValueError("level filter value error!!")
            return LevelFilter(threshold=_level)
        return LevelFilter()

    def _define_args_cmd(self, args_parser):
        comm_cmd = args_parser.add_subparsers(
            dest=self.dest_cmd,
            title="命令",
            description="快捷命令",
            help="命令说明",
            parser_class=ChineseArgumentParser,
        )
        try:
            comm_cmd.required = False
        except AttributeError:
            pass
        cap = comm_cmd.add_parser("cap-screen", aliases=["cs"], help="截屏")
        self.cmd_name_define["cap-screen"] = ["cap-screen", "cs"]
        cap.add_argument("-path", type=str, help="保存目录")

        record = comm_cmd.add_parser("record-video", aliases=["rv"], help="录屏")
        self.cmd_name_define["record-video"] = ["record-video", "rv"]
        record.add_argument("-path", type=str, help="保存目录")

        dump = comm_cmd.add_parser("dump-log", aliases=["dump"], help="导出崩溃日志")
        self.cmd_name_define["dump-log"] = ["dump-log", "dump"]
        dump.add_argument("-type", type=int, default=0, help="0:应用崩溃 1:Native 崩溃")
        dump.add_argument("-maxsize", type=int, default=10, help="最大条数")
        dump.add_argument("-path", type=str, help="保存目录")

        install = comm_cmd.add_parser("install", aliases=["i"], help="安装 apk/hap")
        self.cmd_name_define["install"] = ["install", "i"]
        install.add_argument("-path", type=str, required=True, help="本地安装包路径")

        config = comm_cmd.add_parser("config", help="配置管理")
        self.cmd_name_define["config"] = ["config"]
        config_sub = config.add_subparsers(
            dest="config_action",
            title="配置子命令",
            help="配置子命令说明",
            parser_class=ChineseArgumentParser,
        )
        try:
            config_sub.required = True
        except AttributeError:
            pass
        config_init = config_sub.add_parser("init", help="生成默认配置文件")
        config_init.add_argument("--force", action="store_true", help="覆盖已有配置文件")
        config_sub.add_parser("path", help="显示配置文件路径")

    def build_parser(self):
        desc = "AKLog-{0} (Android & HarmonyOS developer Swiss Army Knife for Log)".format(self.AK_LOG_VERSION)
        args_parser = ChineseArgumentParser(description=desc)
        args_parser.add_argument(
            "-v",
            "--" + self.dest_version,
            action="version",
            version=self.AK_LOG_VERSION,
            help="显示版本号并退出",
        )
        args_parser.add_argument(
            "-d",
            "--" + self.dest_device,
            dest=self.dest_device,
            type=str,
            help="设备序列号（adb）或 target（hdc）；跳过交互式选择",
        )
        self._define_args_package(args_parser)
        self._define_args_tag(args_parser)
        self._define_args_msg(args_parser)
        self._define_args_level(args_parser)
        self._define_args_cmd(args_parser)
        return args_parser

    def parse(self, argv=None):
        parser = self.build_parser()
        args = parser.parse_args(args=argv)
        args_dict = vars(args)
        self._apply_package_default(args_dict)
        return args_dict

    def build_log_printer(self, args):
        color_theme = LogColorTheme(load_config().colors)
        return LogPrintCtr(
            filters=FilterChain(
                [
                    self._build_package_filter(args),
                    self._build_level_filter(args),
                    self._build_tag_filter(args),
                ]
            ),
            msg_processor=self._build_msg_processor(args),
            color_theme=color_theme,
        )

    def run_command(self, platform, args):
        cmd = args[self.dest_cmd]
        if comm_tools.is_empty(cmd):
            return False
        if cmd in self.cmd_name_define["config"]:
            from aklog.cli.config_cmd import run_config_command

            run_config_command(args)
            return True
        if cmd in self.cmd_name_define["cap-screen"]:
            _dir = comm_tools.get_str(args.get("path"))
            if _dir == "null":
                _dir = None
            ScreenCapTools(platform, _dir).do_capture()
            return True
        if cmd in self.cmd_name_define["record-video"]:
            _dir = comm_tools.get_str(args.get("path"))
            if _dir == "null":
                _dir = None
            RecordHelper.do_work(platform, _dir)
            return True
        if cmd in self.cmd_name_define["dump-log"]:
            _dir = comm_tools.get_str(args.get("path"))
            if _dir == "null":
                _dir = None
            DumpCrashLog(
                platform,
                is_ndk=comm_tools.to_int(args.get("type")) != 0,
                dir=_dir,
                max_size=comm_tools.to_int(args.get("maxsize")),
            ).do_work()
            return True
        if cmd in self.cmd_name_define["install"]:
            path = comm_tools.get_str(args.get("path"))
            platform.install_package(path)
            print("install succeed.")
            return True
        print("exe failure==>{0}".format(cmd))
        return True
