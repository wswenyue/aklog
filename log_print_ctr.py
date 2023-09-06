#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author:   wswenyue
@date:     2022/11/10 
"""
from color_print import ColorStrArr, SimpleColorStr, Colors, ColorStr
from content_filter_format import LogPackageFilterFormat, LogTagFilterFormat, LogMsgFilterFormat, LogLevelFilterFormat
from log_info import LogInfo, LogLevelHelper


class LogPrintCtr(object):
    """
    控制日志的打印输出
    """
    _package: LogPackageFilterFormat = None
    _tag: LogTagFilterFormat = None
    _msg: LogMsgFilterFormat = None
    _level: LogLevelFilterFormat = None

    @property
    def package(self) -> LogPackageFilterFormat:
        return self._package

    @package.setter
    def package(self, _package: LogPackageFilterFormat):
        self._package = _package

    @property
    def tag(self) -> LogTagFilterFormat:
        return self._tag

    @tag.setter
    def tag(self, _tag: LogTagFilterFormat):
        self._tag = _tag

    @property
    def msg(self) -> LogMsgFilterFormat:
        return self._msg

    @msg.setter
    def msg(self, _msg: LogMsgFilterFormat):
        self._msg = _msg

    @property
    def level(self) -> LogLevelFilterFormat:
        return self._level

    @level.setter
    def level(self, _level: LogLevelFilterFormat):
        self._level = _level

    def print(self, log: LogInfo):
        if log is None:
            return
        p_package = self.package.format_content(log.get_process_name())
        if not p_package:
            return
        p_level = self.level.format_content(log.get_level_name())
        if not p_level:
            return
        p_tag = self.tag.format_content(log.tag)
        if not p_tag:
            return
        p_msg = self.msg.format_content(log.get_msg_content())
        if not p_msg:
            return
        p_tid = log.get_show_tid()
        p_time = log.time
        p_name = log.get_show_name()
        # msg = "{0}#{1}#{2}#{3}#{4}#{5}".format(p_time, p_name, p_tid, p_level, p_tag, p_msg)
        level = log.get_level()
        if level == LogLevelHelper.DEBUG:
            base_color = Colors.Green
            tag_color = Colors.LightGreen
        elif level == LogLevelHelper.ERROR:
            base_color = Colors.RED
            tag_color = Colors.LightRed
        elif level == LogLevelHelper.WARN:
            base_color = Colors.Yellow
            tag_color = Colors.LightYellow
        elif level == LogLevelHelper.INFO:
            base_color = Colors.Blue
            tag_color = Colors.LightBlue
        elif level == LogLevelHelper.VERBOSE:
            base_color = Colors.Gray
            tag_color = Colors.LightGray
        else:
            base_color = Colors.Gray
            tag_color = Colors.LightGray
        msg = ColorStrArr(base_color)
        msg.add(SimpleColorStr("{0}#{1}#{2}".format(p_time, p_name, p_tid), Colors.Gray))
        level_color = tag_color.copy()
        level_color.style = "underline"
        msg.add(ColorStr(f" {p_level} ", level_color))
        msg.add(ColorStr(f"{p_tag}#", tag_color))
        if isinstance(p_msg, ColorStr):
            msg.add(p_msg)
        else:
            msg.add(ColorStr(p_msg, base_color))
        print(str(msg))
