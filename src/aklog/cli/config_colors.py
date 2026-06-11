#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

import copy

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from aklog.core.color_presets import COLOR_FIELDS, COLOR_PALETTE, PRESETS, get_color_field, set_color_field
from aklog.core.config import default_color_config, load_config, save_config
from aklog.log.preview import render_log_preview
from aklog.log.theme import LogColorTheme

console = Console()


def _is_tty() -> bool:
    import sys

    return sys.stdin.isatty() and sys.stdout.isatty()


def _render_colors_page(draft) -> None:
    console.clear()
    table = Table(title="配色字段")
    table.add_column("Key")
    table.add_column("Value")
    for key in COLOR_FIELDS:
        value = get_color_field(draft, key)
        table.add_row(key, value)
    console.print(table)
    palette = Table(title="色表")
    palette.add_column("Sample")
    palette.add_column("Name")
    for name in COLOR_PALETTE[:16]:
        palette.add_row(Text_block(name), name)
    console.print(palette)
    preview_lines = render_log_preview(LogColorTheme(draft))
    preview = Panel("\n".join(line.plain for line in preview_lines), title="日志预览", border_style="blue")
    console.print(preview)


def Text_block(name: str) -> str:
    return "████ {0}".format(name)


def colors_show() -> None:
    config = load_config()
    theme = LogColorTheme(config.colors)
    for line in render_log_preview(theme):
        console.print(line)


def colors_reset() -> None:
    config = load_config()
    config.colors = default_color_config()
    save_config(config)
    console.print("Colors reset to defaults.")


def colors_get(key: str) -> None:
    config = load_config()
    print(get_color_field(config.colors, key))


def colors_set(key: str, value: str) -> None:
    config = load_config()
    if key not in COLOR_FIELDS:
        raise ValueError("unknown color key: {0}".format(key))
    set_color_field(config.colors, key, value)
    save_config(config)
    console.print("Updated {0}={1}".format(key, value))


def run_colors_editor() -> None:
    if not _is_tty():
        colors_show()
        return
    import questionary

    draft = copy.deepcopy(load_config().colors)
    while True:
        _render_colors_page(draft)
        action = questionary.select(
            "配色编辑",
            choices=[
                "修改字段",
                "应用预设方案",
                "恢复默认",
                "保存并退出",
                "放弃",
            ],
        ).ask()
        if action is None or action == "放弃":
            if questionary.confirm("放弃未保存的修改？", default=False).ask():
                return
            continue
        if action == "保存并退出":
            config = load_config()
            config.colors = draft
            save_config(config)
            console.print("配色已保存。")
            return
        if action == "恢复默认":
            draft = default_color_config()
            continue
        if action == "应用预设方案":
            preset_name = questionary.select("预设", choices=list(PRESETS.keys())).ask()
            if preset_name:
                draft = copy.deepcopy(PRESETS[preset_name]())
            continue
        if action == "修改字段":
            field = questionary.select("字段", choices=COLOR_FIELDS).ask()
            if not field:
                continue
            color = questionary.select(
                "颜色",
                choices=COLOR_PALETTE + ["自定义 #RRGGBB"],
            ).ask()
            if color == "自定义 #RRGGBB":
                custom = questionary.text("输入 #RRGGBB").ask()
                if custom:
                    set_color_field(draft, field, custom.strip())
            elif color:
                set_color_field(draft, field, color)


def run_colors_command(action: str | None, args: dict) -> bool:
    if action is None or action == "edit":
        run_colors_editor()
        return True
    if action == "show":
        colors_show()
        return True
    if action == "reset":
        colors_reset()
        return True
    if action == "get":
        colors_get(str(args["color_key"]))
        return True
    if action == "set":
        colors_set(str(args["color_key"]), str(args["color_value"]))
        return True
    return False
