#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

from rich.style import Style

from aklog.core.config import ColorConfig, LevelColors, default_color_config
from aklog.log.info import LogLevelHelper


class LogColorTheme:
    def __init__(self, color_config: ColorConfig | None = None):
        self._config = color_config or default_color_config()

    @property
    def config(self) -> ColorConfig:
        return self._config

    def _level_colors(self, level: int) -> LevelColors:
        if level == LogLevelHelper.VERBOSE:
            return self._config.verbose
        if level == LogLevelHelper.DEBUG:
            return self._config.debug
        if level == LogLevelHelper.INFO:
            return self._config.info
        if level == LogLevelHelper.WARN:
            return self._config.warn
        if level == LogLevelHelper.ERROR:
            return self._config.error
        return self._config.verbose

    def meta_style(self) -> Style:
        return Style.parse(self._config.meta)

    def level_style(self, level: int) -> Style:
        colors = self._level_colors(level)
        return Style.parse(f"{self._config.level_style} {colors.tag}")

    def tag_style(self, level: int) -> Style:
        return Style.parse(self._level_colors(level).tag)

    def msg_style(self, level: int) -> Style:
        return Style.parse(self._level_colors(level).base)
