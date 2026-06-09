#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field
from typing import Any, Dict

from aklog.core import comm_tools

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib


@dataclass
class LevelColors:
    base: str
    tag: str


@dataclass
class ColorConfig:
    meta: str = "grey50"
    level_style: str = "bold"
    tag_style: str = "bold underline"
    msg_style: str = "bold"
    verbose: LevelColors = field(default_factory=lambda: LevelColors("grey50", "grey62"))
    debug: LevelColors = field(default_factory=lambda: LevelColors("dark_sea_green2", "spring_green2"))
    info: LevelColors = field(default_factory=lambda: LevelColors("steel_blue3", "bright_blue"))
    warn: LevelColors = field(default_factory=lambda: LevelColors("dark_goldenrod", "bright_yellow"))
    error: LevelColors = field(default_factory=lambda: LevelColors("indian_red", "bright_red"))


@dataclass
class AklogConfig:
    colors: ColorConfig = field(default_factory=ColorConfig)


DEFAULT_CONFIG_TEMPLATE = """\
# aklog user configuration
# Docs: https://github.com/wswenyue/aklog#configuration

[colors]
meta = "grey50"
level_style = "bold"
tag_style = "bold underline"
msg_style = "bold"

[colors.verbose]
base = "grey50"
tag = "grey62"

[colors.debug]
base = "dark_sea_green2"
tag = "spring_green2"

[colors.info]
base = "steel_blue3"
tag = "bright_blue"

[colors.warn]
base = "dark_goldenrod"
tag = "bright_yellow"

[colors.error]
base = "indian_red"
tag = "bright_red"

# Future (not used yet):
# [defaults]
# level = "D"
# device = "emulator-5554"
"""


def config_dir() -> str:
    if comm_tools.is_windows_os():
        appdata = os.environ.get("APPDATA", "")
        if appdata:
            return os.path.join(appdata, "aklog")
        return os.path.join(comm_tools.get_user_home_dir(), ".config", "aklog")
    xdg = os.environ.get("XDG_CONFIG_HOME")
    if xdg:
        return os.path.join(xdg, "aklog")
    return os.path.join(comm_tools.get_user_home_dir(), ".config", "aklog")


def config_path() -> str:
    return os.path.join(config_dir(), "config.toml")


def default_color_config() -> ColorConfig:
    return ColorConfig()


def _parse_level_colors(section: Dict[str, Any], key: str, default: LevelColors) -> LevelColors:
    value = section.get(key, {})
    if not isinstance(value, dict):
        return default
    base = value.get("base", default.base)
    tag = value.get("tag", default.tag)
    return LevelColors(base=str(base), tag=str(tag))


def _parse_colors(data: Dict[str, Any]) -> ColorConfig:
    default = default_color_config()
    colors_data = data.get("colors", {})
    if not isinstance(colors_data, dict):
        return default
    return ColorConfig(
        meta=str(colors_data.get("meta", default.meta)),
        level_style=str(colors_data.get("level_style", default.level_style)),
        tag_style=str(colors_data.get("tag_style", default.tag_style)),
        msg_style=str(colors_data.get("msg_style", default.msg_style)),
        verbose=_parse_level_colors(colors_data, "verbose", default.verbose),
        debug=_parse_level_colors(colors_data, "debug", default.debug),
        info=_parse_level_colors(colors_data, "info", default.info),
        warn=_parse_level_colors(colors_data, "warn", default.warn),
        error=_parse_level_colors(colors_data, "error", default.error),
    )


def _is_valid_rich_color(color: str) -> bool:
    from rich.color import Color
    from rich.style import Style

    try:
        Style.parse(color)
        return True
    except Exception:
        try:
            Color.parse(color)
            return True
        except Exception:
            return False


def _safe_color(color: str, fallback: str, label: str, warnings: list) -> str:
    if _is_valid_rich_color(color):
        return color
    warnings.append(f"{label}: invalid color '{color}', using '{fallback}'")
    return fallback


def _validate_color_config(config: ColorConfig) -> ColorConfig:
    default = default_color_config()
    warnings: list = []

    def validate_level(name: str, current: LevelColors, fallback: LevelColors) -> LevelColors:
        return LevelColors(
            base=_safe_color(current.base, fallback.base, f"colors.{name}.base", warnings),
            tag=_safe_color(current.tag, fallback.tag, f"colors.{name}.tag", warnings),
        )

    validated = ColorConfig(
        meta=_safe_color(config.meta, default.meta, "colors.meta", warnings),
        level_style=config.level_style if _is_valid_rich_color(config.level_style) else default.level_style,
        tag_style=config.tag_style if _is_valid_rich_color(config.tag_style) else default.tag_style,
        msg_style=config.msg_style if _is_valid_rich_color(config.msg_style) else default.msg_style,
        verbose=validate_level("verbose", config.verbose, default.verbose),
        debug=validate_level("debug", config.debug, default.debug),
        info=validate_level("info", config.info, default.info),
        warn=validate_level("warn", config.warn, default.warn),
        error=validate_level("error", config.error, default.error),
    )
    if config.level_style != validated.level_style:
        warnings.append(f"colors.level_style: invalid style '{config.level_style}', using '{default.level_style}'")
    if config.tag_style != validated.tag_style:
        warnings.append(f"colors.tag_style: invalid style '{config.tag_style}', using '{default.tag_style}'")
    if config.msg_style != validated.msg_style:
        warnings.append(f"colors.msg_style: invalid style '{config.msg_style}', using '{default.msg_style}'")

    for warning in warnings:
        _print_config_warning(warning)

    return validated


def _print_config_warning(message: str) -> None:
    try:
        from aklog.core.console import print_warning

        print_warning(message)
    except Exception:
        print(f"aklog: warning: {message}", file=sys.stderr)


def load_config() -> AklogConfig:
    path = config_path()
    if not os.path.isfile(path):
        return AklogConfig()
    try:
        with open(path, "rb") as handle:
            data = tomllib.load(handle)
        if not isinstance(data, dict):
            raise ValueError("config root must be a table")
        colors = _validate_color_config(_parse_colors(data))
        return AklogConfig(colors=colors)
    except Exception as exc:
        _print_config_warning(f"failed to load config from {path}: {exc}")
        return AklogConfig()


def init_config_file(force: bool = False) -> tuple[str, bool]:
    """
    Write default config template.

    Returns (path, created). created is False when file exists and force is False.
    """
    path = config_path()
    if os.path.isfile(path) and not force:
        return path, False
    comm_tools.create_dir_not_exists(path)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(DEFAULT_CONFIG_TEMPLATE)
    return path, True
