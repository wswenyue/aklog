#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

import sys

from rich.console import Console
from rich.table import Table

from aklog.cli.config_colors import run_colors_editor
from aklog.cli.config_filter import filter_show, run_filter_command
from aklog.core.config import config_path, load_config, migrate_config_file

console = Console()


def _is_tty() -> bool:
    return sys.stdin.isatty() and sys.stdout.isatty()


def run_config_console() -> None:
    if not _is_tty():
        config = load_config()
        console.print("Config path: {0}".format(config_path()))
        filter_show(config.filter.active)
        return
    import questionary

    while True:
        action = questionary.select(
            "aklog 配置控制台",
            choices=[
                "查看当前配置",
                "编辑配色",
                "切换过滤方案",
                "编辑过滤方案",
                "新建过滤方案",
                "删除过滤方案",
                "迁移配置（插入 filter 段）",
                "显示配置文件路径",
                "退出",
            ],
        ).ask()
        if action is None or action == "退出":
            return
        if action == "查看当前配置":
            config = load_config()
            table = Table(title="当前配置")
            table.add_column("项")
            table.add_column("值")
            table.add_row("active profile", config.filter.active)
            table.add_row("profiles", ", ".join(sorted(config.filter.profiles.keys())))
            table.add_row("config path", config_path())
            console.print(table)
            filter_show(config.filter.active)
        elif action == "编辑配色":
            run_colors_editor()
        elif action == "切换过滤方案":
            config = load_config()
            names = sorted(config.filter.profiles.keys())
            choice = questionary.select("方案", choices=names).ask()
            if choice:
                run_filter_command("use", {"filter_name": choice})
        elif action == "编辑过滤方案":
            config = load_config()
            names = sorted(config.filter.profiles.keys())
            choice = questionary.select("方案", choices=names).ask()
            if choice:
                run_filter_command("edit", {"filter_name": choice})
        elif action == "新建过滤方案":
            name = questionary.text("新方案名称").ask()
            if name:
                run_filter_command("new", {"filter_name": name.strip()})
        elif action == "删除过滤方案":
            config = load_config()
            names = sorted(config.filter.profiles.keys())
            choice = questionary.select("删除方案", choices=names).ask()
            if choice:
                run_filter_command("delete", {"filter_name": choice})
        elif action == "迁移配置（插入 filter 段）":
            path, created = migrate_config_file()
            if created:
                console.print("Migrated config: {0}".format(path))
            else:
                console.print("No migration needed: {0}".format(path))
        elif action == "显示配置文件路径":
            console.print(config_path())
