#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author:   wswenyue
@date:     2022/11/10
"""

from typing import Optional

from aklog.core.color_print import Colors, ColorStr, ColorStrArr, SimpleColorStr
from aklog.log.filter import FilterChain, MsgProcessor
from aklog.log.info import LogInfo, LogLevelHelper


class LogPrintCtr:
    """
    控制日志的打印输出
    """

    def __init__(
        self,
        filters: FilterChain,
        msg_processor: Optional[MsgProcessor] = None,
    ):
        self._filters = filters
        self._msg_processor = msg_processor or MsgProcessor()

    @property
    def filters(self) -> FilterChain:
        return self._filters

    @property
    def msg_processor(self) -> MsgProcessor:
        return self._msg_processor

    def print(self, log: LogInfo):
        if log is None:
            return
        if not self._filters.accept(log):
            return
        p_msg = self._msg_processor.process(log.get_msg_content())
        if not p_msg:
            return
        p_level = log.get_level_name()
        p_tag = log.tag
        p_tid = log.get_show_tid()
        p_time = log.time
        p_name = log.get_show_name()
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
        msg.add(SimpleColorStr("{0}#{1}#{2}#".format(p_time, p_name, p_tid), Colors.Gray))
        level_color = tag_color.copy()
        level_color.style = "underline"
        msg.add(ColorStr(f"{p_level}", level_color))
        msg.add(ColorStr(f"#{p_tag}#", tag_color))
        if isinstance(p_msg, ColorStr):
            msg.add(p_msg)
        else:
            msg.add(ColorStr(p_msg, base_color))
        print(str(msg))
