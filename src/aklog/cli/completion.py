#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import

import argparse

from argcomplete.completers import ChoicesCompleter, FilesCompleter

from aklog.device.manager import list_all_devices

_LEVEL_CHOICES = ["V", "D", "I", "W", "E", "2", "3", "4", "5", "6"]
_DUMP_TYPE_CHOICES = ["0", "1"]


def _device_completer(prefix, **kwargs):
    try:
        devices = list_all_devices()
    except Exception:
        return []
    return [d.device_id for d in devices if d.device_id.startswith(prefix)]


def _iter_parsers(parser):
    yield parser
    for action in parser._actions:
        if isinstance(action, argparse._SubParsersAction):
            for sub in action.choices.values():
                for child in _iter_parsers(sub):
                    yield child


def register_completers(parser):
    level_completer = ChoicesCompleter(_LEVEL_CHOICES)
    type_completer = ChoicesCompleter(_DUMP_TYPE_CHOICES)
    install_path_completer = FilesCompleter(".apk", ".hap")

    for sub in _iter_parsers(parser):
        for action in sub._actions:
            if action.dest == "device":
                action.completer = _device_completer
            elif action.dest == "level":
                action.completer = level_completer
            elif action.dest == "type" and "-type" in action.option_strings:
                action.completer = type_completer
            elif action.dest == "path" and action.required:
                action.completer = install_path_completer
