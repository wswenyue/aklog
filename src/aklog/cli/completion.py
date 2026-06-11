#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import

import argparse

from argcomplete.completers import ChoicesCompleter, FilesCompleter

from aklog.core.color_presets import COLOR_FIELDS
from aklog.core.config import load_config
from aklog.core.filter_config import FILTER_FIELD_KEYS
from aklog.device.manager import list_all_devices

_LEVEL_CHOICES = ["V", "D", "I", "W", "E", "2", "3", "4", "5", "6"]
_DUMP_TYPE_CHOICES = ["0", "1"]
_FILTER_KEYS = list(FILTER_FIELD_KEYS) + [
    "android.{0}".format(k) for k in FILTER_FIELD_KEYS if k != "platform"
] + [
    "harmony.{0}".format(k) for k in FILTER_FIELD_KEYS if k != "platform"
]


def _device_completer(prefix, **kwargs):
    try:
        devices = list_all_devices()
    except Exception:
        return []
    return [d.device_id for d in devices if d.device_id.startswith(prefix)]


def _profile_completer(prefix, **kwargs):
    try:
        config = load_config()
        names = list(config.filter.profiles.keys())
    except Exception:
        return []
    return [n for n in names if n.startswith(prefix)]


def _filter_key_completer(prefix, **kwargs):
    return [k for k in _FILTER_KEYS if k.startswith(prefix)]


def _color_key_completer(prefix, **kwargs):
    return [k for k in COLOR_FIELDS if k.startswith(prefix)]


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
            elif action.dest == "filter_name":
                action.completer = _profile_completer
            elif action.dest == "filter_path":
                action.completer = _filter_key_completer
            elif action.dest == "color_key":
                action.completer = _color_key_completer
