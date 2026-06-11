#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import Dict, Iterable, List, Set

from aklog.core.config import AklogConfig
from aklog.core.filter_config import FILTER_FIELD_KEYS, PLATFORM_OVERRIDE_KEYS, FilterProfile

FILTER_FLAG_MAP = {
    "-p": "package",
    "--package": "package",
    "-pa": "package_all",
    "--package_all": "package_all",
    "-pc": "package_current_top",
    "--package_current_top": "package_current_top",
    "-pn": "package_not",
    "--package_not": "package_not",
    "-t": "tag",
    "--tag": "tag",
    "-te": "tag_exact",
    "--tag_exact": "tag_exact",
    "-tn": "tag_not",
    "--tag_not": "tag_not",
    "-ten": "tag_not_exact",
    "--tag_not_exact": "tag_not_exact",
    "-m": "msg",
    "--msg": "msg",
    "-me": "msg_exact",
    "--msg_exact": "msg_exact",
    "-mn": "msg_not",
    "--msg_not": "msg_not",
    "-men": "msg_not_exact",
    "--msg_not_exact": "msg_not_exact",
    "-l": "level",
    "--level": "level",
}


def detect_explicit_filter_flags(argv: Iterable[str] | None) -> Set[str]:
    if not argv:
        return set()
    explicit: Set[str] = set()
    tokens = list(argv)
    idx = 0
    while idx < len(tokens):
        token = tokens[idx]
        if token in FILTER_FLAG_MAP:
            explicit.add(FILTER_FLAG_MAP[token])
        idx += 1
    return explicit


def _merge_lists(base_list: List[str], override_list: List[str]) -> List[str]:
    if override_list:
        return list(override_list)
    return list(base_list)


def resolve_effective_filter(profile: FilterProfile, platform: str | None = None) -> FilterProfile:
    effective = profile.copy()
    if not platform:
        return effective
    platform_key = platform.strip().lower()
    if platform_key not in PLATFORM_OVERRIDE_KEYS:
        return effective
    override = profile.platform_overrides.get(platform_key)
    if override is None:
        return effective
    if override.package_mode is not None:
        effective.package_mode = override.package_mode
    effective.package = _merge_lists(effective.package, override.package)
    effective.tag = _merge_lists(effective.tag, override.tag)
    if override.tag_exact is not None:
        effective.tag_exact = override.tag_exact
    effective.tag_exclude = _merge_lists(effective.tag_exclude, override.tag_exclude)
    effective.tag_exclude_exact = _merge_lists(effective.tag_exclude_exact, override.tag_exclude_exact)
    effective.msg = _merge_lists(effective.msg, override.msg)
    if override.msg_exact is not None:
        effective.msg_exact = override.msg_exact
    effective.msg_exclude = _merge_lists(effective.msg_exclude, override.msg_exclude)
    effective.msg_exclude_exact = _merge_lists(effective.msg_exclude_exact, override.msg_exclude_exact)
    return effective


def get_active_profile(config: AklogConfig) -> FilterProfile:
    config.filter.ensure_default_profile()
    return config.filter.profiles[config.filter.active].copy()


def get_device_platform_pref(config: AklogConfig) -> str:
    profile = get_active_profile(config)
    return (profile.platform or "").strip().lower()


def effective_filter_to_args(effective: FilterProfile) -> Dict:
    args: Dict = {
        "package": None,
        "package_not": None,
        "package_all": False,
        "package_current_top": False,
        "tag": None,
        "tag_exact": None,
        "tag_not": None,
        "tag_not_exact": None,
        "msg": None,
        "msg_exact": None,
        "msg_not": None,
        "msg_not_exact": None,
        "level": None,
    }
    mode = (effective.package_mode or "top").lower()
    if mode == "target" and effective.package:
        args["package"] = list(effective.package)
    elif mode == "exclude" and effective.package:
        args["package_not"] = list(effective.package)
    elif mode == "all":
        args["package_all"] = True
    elif mode == "top":
        args["package_current_top"] = True
    if effective.tag:
        if effective.tag_exact:
            args["tag_exact"] = list(effective.tag)
        else:
            args["tag"] = list(effective.tag)
    if effective.tag_exclude:
        args["tag_not"] = list(effective.tag_exclude)
    if effective.tag_exclude_exact:
        args["tag_not_exact"] = list(effective.tag_exclude_exact)
    if effective.msg:
        if effective.msg_exact:
            args["msg_exact"] = list(effective.msg)
        else:
            args["msg"] = list(effective.msg)
    if effective.msg_exclude:
        args["msg_not"] = list(effective.msg_exclude)
    if effective.msg_exclude_exact:
        args["msg_not_exact"] = list(effective.msg_exclude_exact)
    return args


def merge_into_args(args_dict: Dict, config: AklogConfig, platform: str | None, explicit_flags: Set[str]) -> Dict:
    profile = get_active_profile(config)
    effective = resolve_effective_filter(profile, platform)
    config_args = effective_filter_to_args(effective)
    package_flags = {"package", "package_not", "package_all", "package_current_top"}
    if not explicit_flags.intersection(package_flags):
        for key in package_flags:
            args_dict[key] = config_args[key]
    for key in FILTER_FIELD_KEYS:
        if key in ("platform", "package_mode"):
            continue
        dest = key
        if key == "tag_exclude":
            dest = "tag_not"
        elif key == "tag_exclude_exact":
            dest = "tag_not_exact"
        elif key == "msg_exclude":
            dest = "msg_not"
        elif key == "msg_exclude_exact":
            dest = "msg_not_exact"
        if dest in explicit_flags:
            continue
        if (dest in config_args and config_args[dest] is not None) or (
            dest in config_args and config_args[dest] is True
        ):
            args_dict[dest] = config_args[dest]
    return args_dict
