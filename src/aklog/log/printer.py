#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author:   wswenyue
@date:     2022/11/10
"""

import threading
from typing import Optional

from rich.text import Text

from aklog.core.console import print_styled
from aklog.log.filter import FilterChain, MsgProcessor
from aklog.log.info import LogInfo
from aklog.log.theme import LogColorTheme

LOG_FIELD_SEP = " | "


class LogPrintCtr:
    """
    控制日志的打印输出
    """

    def __init__(
        self,
        filters: FilterChain,
        msg_processor: Optional[MsgProcessor] = None,
        color_theme: Optional[LogColorTheme] = None,
    ):
        self._filters = filters
        self._msg_processor = msg_processor or MsgProcessor()
        self._color_theme = color_theme or LogColorTheme()
        self._lock = threading.Lock()
        self._display_enabled = True

    @property
    def filters(self) -> FilterChain:
        return self._filters

    @property
    def msg_processor(self) -> MsgProcessor:
        return self._msg_processor

    @property
    def color_theme(self) -> LogColorTheme:
        return self._color_theme

    def set_display_enabled(self, enabled: bool) -> None:
        self._display_enabled = enabled

    def apply_filter_state(self, state, cli_builder) -> None:
        args = state.to_args_dict()
        with self._lock:
            self._filters.replace_filters(
                [
                    cli_builder._build_package_filter(args),
                    cli_builder._build_level_filter(args),
                    cli_builder._build_tag_filter(args),
                ]
            )
            self._msg_processor = cli_builder._build_msg_processor(args)

    def print(self, log: LogInfo):
        if log is None or not self._display_enabled:
            return
        with self._lock:
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
            theme = self._color_theme
            line = Text()
            line.append(
                "{0}{1}{2}{1}{3}{1}".format(p_time, LOG_FIELD_SEP, p_name, p_tid),
                style=theme.meta_style(),
            )
            line.append(p_level, style=theme.level_style(level))
            line.append("{0}{1}{0}".format(LOG_FIELD_SEP, p_tag), style=theme.tag_style(level))
            if isinstance(p_msg, Text):
                line.append(p_msg)
            else:
                line.append(str(p_msg), style=theme.msg_style(level))
            print_styled(line)
