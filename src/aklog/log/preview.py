#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import List

from rich.text import Text

from aklog.log.info import LogInfo, LogLevelHelper
from aklog.log.printer import LOG_FIELD_SEP
from aklog.log.theme import LogColorTheme


def _sample_log(level_name: str, tag: str, msg: str) -> LogInfo:
    log = LogInfo("01-01", "12:34:56.789", "12345", "12345", level_name[0], tag)
    log.append_msg_content(msg)
    return log


SAMPLE_SPECS = [
    ("VERBOSE", "System", "boot completed"),
    ("DEBUG", "Network", "request ok"),
    ("INFO", "MainActivity", "onResume"),
    ("WARN", "Battery", "low power"),
    ("ERROR", "Crash", "NullPointerException"),
]


def render_log_line(log: LogInfo, theme: LogColorTheme) -> Text:
    level = log.get_level()
    p_msg = log.get_msg_content()
    line = Text()
    line.append(
        "{0}{1}MyApp{1}{2}{1}".format(log.time, LOG_FIELD_SEP, log.get_show_tid()),
        style=theme.meta_style(),
    )
    line.append(log.get_level_name(), style=theme.level_style(level))
    line.append("{0}{1}{0}".format(LOG_FIELD_SEP, log.tag), style=theme.tag_style(level))
    line.append(str(p_msg), style=theme.msg_style(level))
    return line


def render_log_preview(theme: LogColorTheme) -> List[Text]:
    lines: List[Text] = []
    for level_name, tag, msg in SAMPLE_SPECS:
        log = _sample_log(level_name, tag, msg)
        if log.get_level() == LogLevelHelper.UNKNOWN:
            continue
        lines.append(render_log_line(log, theme))
    return lines
