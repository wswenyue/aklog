#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author:   wswenyue
@date:     2022/11/10 
"""
import re

import color_print
import comm_tools
from log_print_ctr import LogPrintCtr
from log_info import LogInfo


class LogMsgParser(object):
    # [ <datetime> <pid>:<tid> <priority>/<tag> ]
    # [ 08-28 22:39:39.974  1785: 1832 D/HeadsetStateMachine ]
    PATTERN_HEAD = re.compile(r"^\[\s*(\d{2}-\d{2})\s*(\d{2}:\d{2}:\d{2}.\d+)\s*(\d+):\s*(\d+)\s*([IDEVW])\/(.*)\]$")
    log = None

    def __init__(self, _log_printer: LogPrintCtr = None):
        self._log_printer = _log_printer

    @staticmethod
    def _build_log_info(group) -> LogInfo:
        return LogInfo(
            _date=comm_tools.get_str(group[0]),
            _time=comm_tools.get_str(group[1]),
            _pid=comm_tools.get_str(group[2]),
            _tid=comm_tools.get_str(group[3]),
            _priority=comm_tools.get_str(group[4]),
            _tag=comm_tools.get_str(group[5]))

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
