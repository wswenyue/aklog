#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

import signal
import sys
import threading
from enum import Enum
from typing import Callable

from aklog.cli.config_filter import load_filter_state_for_device, save_filter_state_to_config
from aklog.cli.filter_editor import run_filter_field_editor
from aklog.cli.runtime_help import show_help_overlay
from aklog.core.config import load_config
from aklog.core.console import print_error, print_message
from aklog.log.filter_state import FilterState


class RuntimeMode(Enum):
    STREAM = "STREAM"
    FILTER = "FILTER"
    COMMAND = "COMMAND"
    HELP = "HELP"


class RuntimeContext:
    def __init__(self, device_label: str, device_platform: str, filter_state: FilterState):
        self.device_label = device_label
        self.device_platform = device_platform
        self.filter_state = filter_state
        self.mode = RuntimeMode.STREAM
        self.previous_mode = RuntimeMode.STREAM

    def status_text(self) -> str:
        return "[{0}] {1} | {2} | F1帮助 F2过滤 F3方案".format(
            self.mode.value, self.device_label, self.filter_state.summary()
        )


def _is_interactive_enabled(no_interactive: bool) -> bool:
    if no_interactive:
        return False
    return sys.stdin.isatty() and sys.stdout.isatty()


def _parse_command(line: str, ctx: RuntimeContext) -> bool:
    text = line.strip()
    if not text:
        return False
    if text.startswith(":"):
        text = text[1:].strip()
    if text in ("q", "quit", "exit"):
        raise SystemExit(0)
    if text == "w":
        save_filter_state_to_config(ctx.filter_state, ctx.device_platform)
        print_message("已保存到配置。")
        return True
    parts = text.split(None, 1)
    cmd = parts[0].lower()
    arg = parts[1].strip() if len(parts) > 1 else ""
    if cmd == "profile" and arg:
        config = load_config()
        if arg not in config.filter.profiles:
            print_error("方案不存在: {0}".format(arg))
            return True
        ctx.filter_state = load_filter_state_for_device(arg, ctx.device_platform)
        ctx.filter_state.dirty = True
        return True
    if cmd == "tag" and arg:
        ctx.filter_state.tag = [arg]
        ctx.filter_state.dirty = True
        return True
    if cmd == "msg" and arg:
        ctx.filter_state.msg = [arg]
        ctx.filter_state.dirty = True
        return True
    if cmd == "pkg":
        if arg in ("top", "all"):
            ctx.filter_state.package_mode = arg
            ctx.filter_state.package = []
        else:
            ctx.filter_state.package_mode = "target"
            ctx.filter_state.package = [arg]
        ctx.filter_state.dirty = True
        return True
    print_error("未知命令: {0}".format(text))
    return True


def _read_key() -> str | None:
    try:
        import readchar

        ch = readchar.readkey()
        if ch in ("\x1bOP", "\x1b[11~"):
            return "F1"
        if ch in ("\x1bOQ", "\x1b[12~"):
            return "F2"
        if ch in ("\x1bOR", "\x1b[13~"):
            return "F3"
        if ch == ":":
            return ":"
        if ch == "?":
            return "?"
        if ch in ("\x1b",):
            return "ESC"
        return ch
    except Exception:
        return None


def _print_status(ctx: RuntimeContext) -> None:
    try:
        sys.stdout.write("\n" + ctx.status_text() + "\n")
        sys.stdout.flush()
    except Exception:
        pass


def _apply_profile_select(ctx: RuntimeContext) -> None:
    import questionary

    config = load_config()
    names = sorted(config.filter.profiles.keys())
    choice = questionary.select("切换过滤方案", choices=names).ask()
    if choice:
        ctx.filter_state = load_filter_state_for_device(choice, ctx.device_platform)
        ctx.filter_state.dirty = False


class RuntimeController:
    def __init__(
        self,
        ctx: RuntimeContext,
        log_printer,
        cli,
        apply_filters: Callable[[FilterState], None],
    ):
        self.ctx = ctx
        self.log_printer = log_printer
        self.cli = cli
        self.apply_filters = apply_filters
        self._keyboard_stop = threading.Event()

    def _set_stream_display(self, enabled: bool) -> None:
        self.log_printer.set_display_enabled(enabled)

    def _keyboard_loop(self) -> None:
        while not self._keyboard_stop.is_set():
            key = _read_key()
            if key is None:
                continue
            if self.ctx.mode == RuntimeMode.HELP:
                self._close_help()
                continue
            if key == "F1" or (key == "?" and self.ctx.mode != RuntimeMode.COMMAND):
                self._open_help()
            elif key == "F2" and self.ctx.mode == RuntimeMode.STREAM:
                self._enter_filter()
            elif key == "F3" and self.ctx.mode == RuntimeMode.STREAM:
                self._enter_filter_select_profile()
            elif key == ":" and self.ctx.mode == RuntimeMode.STREAM:
                self._enter_command()
            elif key == "ESC" and self.ctx.mode in (RuntimeMode.FILTER, RuntimeMode.COMMAND):
                self.ctx.mode = RuntimeMode.STREAM
                self._set_stream_display(True)
                _print_status(self.ctx)

    def _open_help(self) -> None:
        self.ctx.previous_mode = self.ctx.mode
        self.ctx.mode = RuntimeMode.HELP
        self._set_stream_display(False)
        show_help_overlay(self.ctx.device_label, self.ctx.filter_state, self.ctx.previous_mode.value)
        try:
            import readchar

            readchar.readkey()
        except Exception:
            pass
        self._close_help()

    def _close_help(self) -> None:
        self.ctx.mode = self.ctx.previous_mode
        self._set_stream_display(self.ctx.mode == RuntimeMode.STREAM)
        _print_status(self.ctx)

    def _enter_filter(self) -> None:
        self.ctx.mode = RuntimeMode.FILTER
        self._set_stream_display(False)
        updated = run_filter_field_editor(self.ctx.filter_state, scope=self.ctx.device_platform or "global")
        if updated:
            self.ctx.filter_state = updated
            self.ctx.filter_state.dirty = True
            self.apply_filters(self.ctx.filter_state)
        self.ctx.mode = RuntimeMode.STREAM
        self._set_stream_display(True)
        _print_status(self.ctx)

    def _enter_filter_select_profile(self) -> None:
        self._set_stream_display(False)
        _apply_profile_select(self.ctx)
        self.apply_filters(self.ctx.filter_state)
        self._set_stream_display(True)
        _print_status(self.ctx)

    def _enter_command(self) -> None:
        self.ctx.mode = RuntimeMode.COMMAND
        self._set_stream_display(False)
        try:
            line = input("\n:")
            _parse_command(line, self.ctx)
            self.apply_filters(self.ctx.filter_state)
        except (EOFError, KeyboardInterrupt):
            pass
        self.ctx.mode = RuntimeMode.STREAM
        self._set_stream_display(True)
        _print_status(self.ctx)

    def start(self) -> None:
        thread = threading.Thread(target=self._keyboard_loop, name="aklog-keyboard", daemon=True)
        thread.start()
        _print_status(self.ctx)

    def stop(self) -> None:
        self._keyboard_stop.set()
        self._set_stream_display(True)


def run_with_runtime_ui(platform, log_printer, cli, level_arg=None, no_interactive: bool = False):
    from aklog.app.info import AppInfoHelper
    from aklog.core import cmd_runner
    from aklog.core.comm_tools import get_str

    config = load_config()
    state = load_filter_state_for_device(config.filter.active, platform.platform)
    device_label = "{0}:{1}".format(platform.platform, platform.device_id)

    controller: RuntimeController | None = None
    if _is_interactive_enabled(no_interactive):
        ctx = RuntimeContext(device_label, platform.platform, state)

        def apply_filters(filter_state: FilterState) -> None:
            log_printer.apply_filter_state(filter_state, cli)

        controller = RuntimeController(ctx, log_printer, cli, apply_filters)
        controller.start()

    pro_holder = {"pro": None}

    def _cleanup(*_args):
        if controller:
            controller.stop()
        pro = pro_holder.get("pro")
        if pro:
            try:
                pro.terminate()
            except Exception:
                pass

    old_int = signal.getsignal(signal.SIGINT)
    try:
        signal.signal(signal.SIGINT, _cleanup)
    except Exception:
        pass

    platform.check_connect()
    AppInfoHelper.start(platform)
    level = None
    if level_arg:
        level = get_str(level_arg[0]) if isinstance(level_arg, list) else get_str(level_arg)
    pro = platform.start_log_stream(level=level)
    pro_holder["pro"] = pro
    parser = platform.create_log_parser(log_printer)
    read_line = cmd_runner.read_stdout_line(pro.stdout)
    err_code = pro.poll()
    _line = None
    try:
        while err_code is None:
            try:
                _line = read_line()
                if _line:
                    parser.parser(get_str(_line).strip())
            except Exception as e:
                print_error("===========parser error===============\n{0}".format(e))
                if _line:
                    print("==>{0}<==".format(get_str(_line).strip()))
            err_code = pro.poll()
        if parser.log and log_printer:
            log_printer.print(parser.log)
    finally:
        if controller:
            controller.stop()
        try:
            signal.signal(signal.SIGINT, old_int)
        except Exception:
            pass
