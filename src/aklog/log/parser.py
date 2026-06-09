#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author:   wswenyue
@date:     2022/11/10
"""

import re

from aklog.core import color_print, comm_tools
from aklog.log.info import LogInfo
from aklog.log.printer import LogPrintCtr


class LogMsgParser:
    # [ <datetime> <pid>:<tid> <priority>/<tag> ]
    # [ 08-28 22:39:39.974  1785: 1832 D/HeadsetStateMachine ]
    PATTERN_HEAD = re.compile(r"^\[\s*(\d{2}-\d{2})\s*(\d{2}:\d{2}:\d{2}.\d+)\s*(\d+):\s*(\d+)\s*([IDEVW])\/(.*)\]$")
    log = None

    def __init__(self, _log_printer: LogPrintCtr = None):
        self._log_printer = _log_printer

    @staticmethod
    def _build_log_info(group) -> LogInfo:
        return LogInfo(
            _date=group[0],
            _time=group[1],
            _pid=group[2],
            _tid=group[3],
            _priority=group[4],
            _tag=group[5],
        )

    def parser(self, msg):
        if comm_tools.is_empty(msg):
            return
        group = self.parser_head(msg)
        if group:
            if self.log:
                self._log_printer.print(self.log)
                self.log = None
            self.log = LogMsgParser._build_log_info(group)
        else:
            if self.log:
                self.log.append_msg_content(msg)
            else:
                color_print.light_gray(">>>>" + str(msg).strip())

    def parser_head(self, _msg):
        match = self.PATTERN_HEAD.search(_msg)
        if match:
            return match.groups()
        else:
            return None


class HilogMsgParser:
    # 04-19 17:02:14.735  5394  5394 I A03200/testTag: message
    PATTERN_HEAD = re.compile(
        r"^(\d{2}-\d{2})\s+(\d{2}:\d{2}:\d{2}\.\d+)\s+(\d+)\s+(\d+)\s+([DIWEFV])\s+([^:]+):\s*(.*)$"
    )
    log = None

    def __init__(self, _log_printer=None):
        self._log_printer = _log_printer

    @staticmethod
    def _build_log_info(group):
        tag = group[5]
        if "/" in tag:
            tag = tag.split("/", 1)[1]
        msg = group[6]
        info = LogInfo(
            _date=group[0],
            _time=group[1],
            _pid=group[2],
            _tid=group[3],
            _priority=group[4],
            _tag=tag,
        )
        if comm_tools.is_not_empty(msg):
            info.append_msg_content(msg)
        return info

    def parser(self, msg):
        if comm_tools.is_empty(msg):
            return
        group = self.parser_head(msg)
        if group:
            if self.log:
                self._log_printer.print(self.log)
                self.log = None
            self.log = HilogMsgParser._build_log_info(group)
            if self.log.get_msg_content():
                self._log_printer.print(self.log)
                self.log = None
        else:
            if self.log:
                self.log.append_msg_content(msg)
            else:
                color_print.light_gray(">>>>" + str(msg).strip())

    def parser_head(self, _msg):
        match = self.PATTERN_HEAD.search(_msg)
        if match:
            return match.groups()
        return None
