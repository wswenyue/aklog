#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

from rich.console import Console
from rich.text import Text

_console = Console(stderr=False, highlight=False)


def get_console() -> Console:
    return _console


def print_styled(text: Text) -> None:
    _console.print(text)


def print_message(msg: str, style: str = "") -> None:
    _console.print(msg, style=style or None)


def print_error(msg: str) -> None:
    _console.print(msg, style="red")


def print_green(msg: str) -> None:
    _console.print(msg, style="green")


def print_dim(msg: str) -> None:
    _console.print(msg, style="grey50")


def print_warning(msg: str) -> None:
    _console.print(f"aklog: warning: {msg}", style="yellow")
