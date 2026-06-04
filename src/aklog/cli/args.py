#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

import argparse

from aklog.build_meta import GIT_TAG
from aklog.core import comm_tools
from aklog.log.filters import (
    LogLevelFilterFormat,
    LogMsgFilterFormat,
    LogPackageFilterFormat,
    LogTagFilterFormat,
    PackageFilterType,
)
from aklog.log.format import JsonValueFormat
from aklog.log.info import LogLevelHelper
from aklog.log.printer import LogPrintCtr
from aklog.tools.dump_crash import DumpCrashLog
from aklog.tools.record_video import RecordHelper
from aklog.tools.screen_cap import ScreenCapTools


def _to_str_arr(obj):
    result = []
    for _target in comm_tools.get_iterable(obj):
        if comm_tools.is_not_empty(_target):
            result.append(comm_tools.get_str(_target))
    return result


class AkLogCli:
    dest_version = "version"
    dest_device = "device"
    dest_package = "package"
    dest_package_all = "package_all"
    dest_package_current_top = "package_current_top"
    dest_package_not = "package_not"
    dest_tag = "tag"
    dest_tag_not = "tag_not"
    dest_tag_not_fuzzy = "tag_not_fuzzy"
    dest_tag_exact = "tag_exact"
    dest_msg = "msg"
    dest_msg_not = "msg_not"
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
            help="Match logs for current foreground app (default when no package filter)",
            action="store_true",
        )
        args_package.add_argument(
            "-pa",
            "--" + self.dest_package_all,
            dest=self.dest_package_all,
            help="Show logs from all packages",
            action="store_true",
        )
        args_package.add_argument(
            "-p",
            "--" + self.dest_package,
            dest=self.dest_package,
            help="Match specified package name(s)",
            type=str,
            nargs="+",
        )
        args_package.add_argument(
            "-pn",
            "--" + self.dest_package_not,
            dest=self.dest_package_not,
            help="Exclude specified package name(s)",
            type=str,
            nargs="+",
        )

    def _apply_package_default(self, args):
        if args[self.dest_package] or args[self.dest_package_not] or args[self.dest_package_all]:
            return
        args[self.dest_package_current_top] = True

    def _parser_args_package(self, args):
        if args[self.dest_package]:
            return LogPackageFilterFormat(PackageFilterType.TARGET, _to_str_arr(args[self.dest_package]))
        if args[self.dest_package_not]:
            return LogPackageFilterFormat(PackageFilterType.EXCLUDE, _to_str_arr(args[self.dest_package_not]))
        if args[self.dest_package_all]:
            return LogPackageFilterFormat(PackageFilterType.All)
        if args[self.dest_package_current_top]:
            return LogPackageFilterFormat(PackageFilterType.Top)
        return LogPackageFilterFormat(PackageFilterType.Top)

    def _define_args_tag(self, args_parser):
        args_tag_not_group = args_parser.add_mutually_exclusive_group()
        args_tag_not_group.add_argument(
            "-tnf",
            "--" + self.dest_tag_not_fuzzy,
            dest=self.dest_tag_not_fuzzy,
            help="Fuzzy exclude tags",
            type=str,
            nargs="+",
        )
        args_tag_not_group.add_argument(
            "-tn", "--" + self.dest_tag_not, dest=self.dest_tag_not, help="Exclude tags", type=str, nargs="+"
        )
        args_tags = args_parser.add_mutually_exclusive_group()
        args_tags.add_argument("-t", "--" + self.dest_tag, dest=self.dest_tag, help="Match tags", type=str, nargs="+")
        args_tags.add_argument(
            "-te", "--" + self.dest_tag_exact, dest=self.dest_tag_exact, help="Exact match tags", type=str, nargs="+"
        )

    def _parser_args_tag(self, args):
        tag_not_array = None
        is_tag_not_fuzzy = False
        if args[self.dest_tag_not]:
            tag_not_array = _to_str_arr(args[self.dest_tag_not])
        elif args[self.dest_tag_not_fuzzy]:
            tag_not_array = _to_str_arr(args[self.dest_tag_not_fuzzy])
            is_tag_not_fuzzy = True
        if comm_tools.is_empty(tag_not_array):
            tag_not_array = None
        if args[self.dest_tag]:
            return LogTagFilterFormat(
                target=_to_str_arr(args[self.dest_tag]),
                tag_not=tag_not_array,
                is_exact=False,
                is_tag_not_fuzzy=is_tag_not_fuzzy,
            )
        if args[self.dest_tag_exact]:
            return LogTagFilterFormat(
                target=_to_str_arr(args[self.dest_tag_exact]),
                tag_not=tag_not_array,
                is_exact=True,
                is_tag_not_fuzzy=is_tag_not_fuzzy,
            )
        return LogTagFilterFormat(tag_not=tag_not_array, is_tag_not_fuzzy=is_tag_not_fuzzy)

    def _define_args_msg(self, args_parser):
        args_parser.add_argument(
            "-mn",
            "--" + self.dest_msg_not,
            dest=self.dest_msg_not,
            help="Exclude message keywords",
            type=str,
            nargs="+",
        )
        args_msg = args_parser.add_mutually_exclusive_group()
        args_msg.add_argument(
            "-m", "--" + self.dest_msg, dest=self.dest_msg, help="Match message keywords", type=str, nargs="+"
        )
        args_msg.add_argument(
            "-mjson",
            "--" + self.dest_msg_json_value,
            dest=self.dest_msg_json_value,
            help="Match JSON keys in log message",
            type=str,
            nargs="+",
        )

    def _parser_args_msg(self, args):
        msg_not_array = None
        if args[self.dest_msg_not]:
            _array = _to_str_arr(args[self.dest_msg_not])
            if comm_tools.is_not_empty(_array):
                msg_not_array = _array
        if args[self.dest_msg_json_value]:
            _array = _to_str_arr(args[self.dest_msg_json_value])
            if comm_tools.is_empty(_array):
                raise ValueError("msg filter -mjson empty value!!")
            return LogMsgFilterFormat(msg_not=msg_not_array, json_format=JsonValueFormat(_keys=_array))
        if args[self.dest_msg]:
            _array = _to_str_arr(args[self.dest_msg])
            if comm_tools.is_empty(_array):
                raise ValueError("msg filter -m empty value!!")
            return LogMsgFilterFormat(target=_array, msg_not=msg_not_array)
        return LogMsgFilterFormat(msg_not=msg_not_array)

    def _define_args_level(self, args_parser):
        args_parser.add_argument(
            "-l", "--" + self.dest_level, dest=self.dest_level, help="Log level V|D|I|W|E or 2-6", type=str, nargs=1
        )

    def _parser_args_level(self, args):
        if args[self.dest_level]:
            _level = LogLevelHelper.level_code(comm_tools.get_str(_to_str_arr(args[self.dest_level])[0]))
            if _level == LogLevelHelper.UNKNOWN:
                raise ValueError("level filter value error!!")
            return LogLevelFilterFormat(target=_level)
        return LogLevelFilterFormat()

    def _define_args_cmd(self, args_parser):
        comm_cmd = args_parser.add_subparsers(
            dest=self.dest_cmd, title="Commands", description="Shortcut commands", help="Command help"
        )
        try:
            comm_cmd.required = False
        except AttributeError:
            pass
        cap = comm_cmd.add_parser("cap-screen", aliases=["cs"], help="Capture screen")
        self.cmd_name_define["cap-screen"] = ["cap-screen", "cs"]
        cap.add_argument("-path", type=str, help="Save directory")

        record = comm_cmd.add_parser("record-video", aliases=["rv"], help="Record screen video")
        self.cmd_name_define["record-video"] = ["record-video", "rv"]
        record.add_argument("-path", type=str, help="Save directory")

        dump = comm_cmd.add_parser("dump-log", aliases=["dump"], help="Dump crash logs")
        self.cmd_name_define["dump-log"] = ["dump-log", "dump"]
        dump.add_argument("-type", type=int, default=0, help="0:app 1:native")
        dump.add_argument("-maxsize", type=int, default=10, help="Max entries")
        dump.add_argument("-path", type=str, help="Save directory")

        install = comm_cmd.add_parser("install", aliases=["i"], help="Install apk/hap")
        self.cmd_name_define["install"] = ["install", "i"]
        install.add_argument("-path", type=str, required=True, help="Local package path")

    def build_parser(self):
        desc = "AKLog-{0} (Android & HarmonyOS developer Swiss Army Knife for Log)".format(self.AK_LOG_VERSION)
        args_parser = argparse.ArgumentParser(description=desc)
        args_parser.add_argument("-v", "--" + self.dest_version, action="version", version=self.AK_LOG_VERSION)
        args_parser.add_argument(
            "-d",
            "--" + self.dest_device,
            dest=self.dest_device,
            type=str,
            help="Device serial (adb) or target (hdc); skip interactive selection",
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
        log_printer = LogPrintCtr()
        log_printer.package = self._parser_args_package(args)
        log_printer.tag = self._parser_args_tag(args)
        log_printer.msg = self._parser_args_msg(args)
        log_printer.level = self._parser_args_level(args)
        return log_printer

    def run_command(self, platform, args):
        cmd = args[self.dest_cmd]
        if comm_tools.is_empty(cmd):
            return False
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
