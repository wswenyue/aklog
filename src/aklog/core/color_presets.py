#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

from aklog.core.config import ColorConfig, LevelColors

COLOR_PALETTE = [
    "black", "red", "green", "yellow", "blue", "magenta", "cyan", "white",
    "bright_red", "bright_green", "bright_yellow", "bright_blue", "bright_magenta", "bright_cyan",
    "grey50", "grey62", "grey70",
    "dark_sea_green3", "aquamarine1", "steel_blue3", "bright_blue",
    "dark_goldenrod", "bright_yellow", "light_coral", "indian_red1",
    "spring_green2", "orange3", "violet", "turquoise2",
]

COLOR_FIELDS = [
    "meta", "level_style", "tag_style", "msg_style",
    "verbose.base", "verbose.tag", "debug.base", "debug.tag",
    "info.base", "info.tag", "warn.base", "warn.tag", "error.base", "error.tag",
]


def default_preset() -> ColorConfig:
    return ColorConfig()


def high_contrast_preset() -> ColorConfig:
    return ColorConfig(
        meta="grey62",
        verbose=LevelColors("grey50", "grey70"),
        debug=LevelColors("green", "bright_green"),
        info=LevelColors("blue", "bright_cyan"),
        warn=LevelColors("yellow", "bright_yellow"),
        error=LevelColors("red", "bright_red"),
    )


def soft_preset() -> ColorConfig:
    return ColorConfig(
        meta="grey50",
        verbose=LevelColors("grey50", "grey62"),
        debug=LevelColors("dark_sea_green2", "spring_green2"),
        info=LevelColors("steel_blue2", "sky_blue1"),
        warn=LevelColors("dark_goldenrod", "gold1"),
        error=LevelColors("indian_red", "light_coral"),
    )


def mono_preset() -> ColorConfig:
    return ColorConfig(
        meta="grey50",
        level_style="bold",
        tag_style="bold",
        msg_style="",
        verbose=LevelColors("grey50", "grey62"),
        debug=LevelColors("grey58", "grey70"),
        info=LevelColors("grey62", "grey78"),
        warn=LevelColors("grey66", "grey84"),
        error=LevelColors("grey70", "grey93"),
    )


PRESETS = {
    "default": default_preset,
    "high_contrast": high_contrast_preset,
    "soft": soft_preset,
    "mono": mono_preset,
}


def get_color_field(config: ColorConfig, key: str) -> str:
    if "." in key:
        level, field = key.split(".", 1)
        level_colors = getattr(config, level)
        return getattr(level_colors, field)
    return getattr(config, key)


def set_color_field(config: ColorConfig, key: str, value: str) -> None:
    if "." in key:
        level, field = key.split(".", 1)
        level_colors = getattr(config, level)
        setattr(level_colors, field, value)
        return
    setattr(config, key, value)
