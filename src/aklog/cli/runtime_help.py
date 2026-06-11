#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from aklog.log.filter_state import FilterState

console = Console()

RUNTIME_HELP_TEXT = """
运行期快捷键:
  F1 / ?     打开/关闭帮助
  F2         过滤编辑
  F3         切换过滤方案
  :          命令模式
  Esc        返回 STREAM

命令模式:
  :tag Network
  :pkg top|all|com.foo
  :msg keyword
  :profile work
  :w         保存到配置
  :q         退出
"""


def build_help_panel(device_label: str, state: FilterState, mode: str) -> Panel:
    table = Table(show_header=False, box=None)
    table.add_row("设备", device_label)
    table.add_row("模式", mode)
    table.add_row("过滤", state.summary())
    table.add_row("", "")
    table.add_row("快捷键", "F1帮助 F2过滤 F3方案 :命令 Esc返回")
    table.add_row("命令", ":tag :pkg :msg :profile :w :q")
    table.add_row("说明", "暂停期间日志不回放；aklog config console 可离线改配置")
    return Panel(table, title="aklog 运行期帮助", border_style="cyan")


def print_runtime_help_text() -> None:
    print(RUNTIME_HELP_TEXT.strip())


def show_help_overlay(device_label: str, state: FilterState, mode: str) -> None:
    console.clear()
    console.print(build_help_panel(device_label, state, mode))
    console.print("\n[dim]按任意键关闭[/dim]")
