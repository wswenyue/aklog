#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, List

from rich.console import Console
from rich.table import Table

from aklog.core.config import AklogConfig, load_config, save_config
from aklog.core.filter_config import (
    FILTER_FIELD_KEYS,
    PLATFORM_OVERRIDE_KEYS,
    FilterProfile,
    PlatformFilterOverride,
    validate_package_mode,
    validate_platform_pref,
    validate_profile_name,
)
from aklog.core.filter_merge import resolve_effective_filter
from aklog.log.filter_state import FilterState

console = Console()


@dataclass
class FilterPath:
    profile: str
    platform: str | None
    key: str | None


def parse_filter_path(path: str) -> FilterPath:
    parts = path.split(".")
    if not parts:
        raise ValueError("invalid path")
    profile = validate_profile_name(parts[0])
    if len(parts) == 1:
        return FilterPath(profile=profile, platform=None, key=None)
    if len(parts) == 2:
        if parts[1] in PLATFORM_OVERRIDE_KEYS:
            return FilterPath(profile=profile, platform=parts[1], key=None)
        return FilterPath(profile=profile, platform=None, key=parts[1])
    if len(parts) == 3 and parts[1] in PLATFORM_OVERRIDE_KEYS:
        return FilterPath(profile=profile, platform=parts[1], key=parts[2])
    raise ValueError("invalid path: {0}".format(path))


def _parse_bool_value(value: str) -> bool:
    lowered = value.strip().lower()
    if lowered in ("true", "1", "yes"):
        return True
    if lowered in ("false", "0", "no"):
        return False
    raise ValueError("bool value must be true or false")


def _parse_list_value(value: str) -> List[str]:
    if not value.strip():
        return []
    return [part.strip() for part in value.split(",") if part.strip()]


def _get_profile(config: AklogConfig, name: str) -> FilterProfile:
    validate_profile_name(name)
    if name not in config.filter.profiles:
        config.filter.profiles[name] = FilterProfile()
    return config.filter.profiles[name]


def _get_override(profile: FilterProfile, platform: str) -> PlatformFilterOverride:
    if platform not in profile.platform_overrides:
        profile.platform_overrides[platform] = PlatformFilterOverride()
    return profile.platform_overrides[platform]


def _target_object(config: AklogConfig, fpath: FilterPath):
    profile = _get_profile(config, fpath.profile)
    if fpath.platform:
        return _get_override(profile, fpath.platform)
    return profile


def _get_value(obj, key: str) -> Any:
    return getattr(obj, key)


def _set_value(obj, key: str, value: Any) -> None:
    if key == "package_mode":
        value = validate_package_mode(str(value))
    elif key == "platform":
        value = validate_platform_pref(str(value))
    elif key in ("tag_exact", "msg_exact"):
        value = _parse_bool_value(str(value)) if isinstance(value, str) else bool(value)
    elif key in (
        "package",
        "tag",
        "tag_exclude",
        "tag_exclude_exact",
        "msg",
        "msg_exclude",
        "msg_exclude_exact",
    ) and isinstance(value, str):
        value = _parse_list_value(value)
    setattr(obj, key, value)


def filter_get(path: str) -> str:
    config = load_config()
    fpath = parse_filter_path(path)
    if fpath.key is None:
        if fpath.platform:
            override = config.filter.profiles.get(fpath.profile, FilterProfile()).platform_overrides.get(fpath.platform)
            return "present" if override and not override.is_empty() else "empty"
        profile = config.filter.profiles.get(fpath.profile)
        return "missing" if profile is None else "present"
    obj = _target_object(config, fpath)
    value = _get_value(obj, fpath.key)
    if isinstance(value, list):
        return ",".join(value)
    return str(value)


def filter_set(path: str, value: str) -> None:
    config = load_config()
    fpath = parse_filter_path(path)
    if fpath.key is None:
        raise ValueError("key is required for set")
    if fpath.key not in FILTER_FIELD_KEYS:
        raise ValueError("unknown key: {0}".format(fpath.key))
    obj = _target_object(config, fpath)
    _set_value(obj, fpath.key, value)
    save_config(config)


def filter_unset(path: str) -> None:
    config = load_config()
    fpath = parse_filter_path(path)
    profile = _get_profile(config, fpath.profile)
    if fpath.platform and fpath.key is None:
        profile.platform_overrides.pop(fpath.platform, None)
        save_config(config)
        return
    if fpath.key is None:
        raise ValueError("key or platform section required for unset")
    obj = _target_object(config, fpath)
    if fpath.key in ("package", "tag", "tag_exclude", "tag_exclude_exact", "msg", "msg_exclude", "msg_exclude_exact"):
        _set_value(obj, fpath.key, [])
    elif fpath.key in ("tag_exact", "msg_exact"):
        _set_value(obj, fpath.key, False)
    elif fpath.key == "package_mode":
        _set_value(obj, fpath.key, "top")
    elif fpath.key == "platform":
        _set_value(obj, fpath.key, "")
    save_config(config)


def filter_list() -> None:
    config = load_config()
    for name in sorted(config.filter.profiles.keys()):
        marker = " (active)" if name == config.filter.active else ""
        console.print("{0}{1}".format(name, marker))


def filter_show(name: str | None = None) -> None:
    config = load_config()
    profile_name = name or config.filter.active
    profile = config.filter.profiles.get(profile_name)
    if profile is None:
        console.print("[red]Profile not found: {0}[/red]".format(profile_name))
        return
    table = Table(title="Filter profile: {0}".format(profile_name))
    table.add_column("Field")
    table.add_column("Value")
    table.add_row("platform (device pref)", profile.platform or "-")
    table.add_row("package_mode", profile.package_mode)
    table.add_row("package", ",".join(profile.package) or "-")
    table.add_row("tag", ",".join(profile.tag) or "-")
    table.add_row("tag_exact", str(profile.tag_exact))
    table.add_row("tag_exclude", ",".join(profile.tag_exclude) or "-")
    table.add_row("msg", ",".join(profile.msg) or "-")
    table.add_row("msg_exact", str(profile.msg_exact))
    for plat in PLATFORM_OVERRIDE_KEYS:
        override = profile.platform_overrides.get(plat)
        if override and not override.is_empty():
            table.add_row("[{0}] package_mode".format(plat), override.package_mode or "-")
            table.add_row("[{0}] package".format(plat), ",".join(override.package) or "-")
            table.add_row("[{0}] tag".format(plat), ",".join(override.tag) or "-")
    console.print(table)


def filter_use(name: str) -> None:
    config = load_config()
    validate_profile_name(name)
    if name not in config.filter.profiles:
        raise ValueError('profile "{0}" does not exist'.format(name))
    config.filter.active = name
    save_config(config)
    console.print("Active profile: {0}".format(name))


def filter_new(name: str, copy_from: str | None = None) -> None:
    config = load_config()
    validate_profile_name(name)
    if name in config.filter.profiles:
        raise ValueError('profile "{0}" already exists'.format(name))
    source_name = copy_from or config.filter.active
    source = config.filter.profiles.get(source_name, FilterProfile())
    config.filter.profiles[name] = source.copy()
    save_config(config)
    console.print("Created profile: {0}".format(name))


def filter_delete(name: str) -> None:
    config = load_config()
    validate_profile_name(name)
    if len(config.filter.profiles) <= 1:
        raise ValueError("cannot delete the last profile")
    if name not in config.filter.profiles:
        raise ValueError('profile "{0}" does not exist'.format(name))
    del config.filter.profiles[name]
    if config.filter.active == name:
        config.filter.active = "default" if "default" in config.filter.profiles else next(iter(config.filter.profiles))
    save_config(config)
    console.print("Deleted profile: {0}".format(name))


def save_filter_state_to_config(state: FilterState, device_platform: str) -> None:
    config = load_config()
    profile = _get_profile(config, state.profile_name)
    if device_platform in PLATFORM_OVERRIDE_KEYS:
        profile.platform_overrides[device_platform] = state.apply_to_platform_override(device_platform)
    else:
        profile.package_mode = state.package_mode
        profile.package = list(state.package)
        profile.tag = list(state.tag)
        profile.tag_exact = state.tag_exact
        profile.tag_exclude = list(state.tag_exclude)
        profile.tag_exclude_exact = list(state.tag_exclude_exact)
        profile.msg = list(state.msg)
        profile.msg_exact = state.msg_exact
        profile.msg_exclude = list(state.msg_exclude)
        profile.msg_exclude_exact = list(state.msg_exclude_exact)
    save_config(config)
    state.dirty = False


def load_filter_state_for_device(profile_name: str, device_platform: str) -> FilterState:
    config = load_config()
    profile = config.filter.profiles.get(profile_name, FilterProfile())
    effective = resolve_effective_filter(profile, device_platform)
    return FilterState.from_filter_profile(effective, profile_name, device_platform)


def run_filter_command(action: str, args: dict) -> bool:
    if action == "list":
        filter_list()
        return True
    if action == "show":
        filter_name = args.get("filter_name")
        filter_show(str(filter_name) if isinstance(filter_name, str) else None)
        return True
    if action == "use":
        filter_use(str(args["filter_name"]))
        return True
    if action == "get":
        print(filter_get(str(args["filter_path"])))
        return True
    if action == "set":
        filter_path = str(args["filter_path"])
        filter_set(filter_path, str(args["filter_value"]))
        console.print("Updated {0}".format(filter_path))
        return True
    if action == "unset":
        filter_path = str(args["filter_path"])
        filter_unset(filter_path)
        console.print("Unset {0}".format(filter_path))
        return True
    if action == "new":
        copy_from = args.get("copy_from")
        filter_new(
            str(args["filter_name"]),
            str(copy_from) if isinstance(copy_from, str) else None,
        )
        return True
    if action == "delete":
        filter_delete(str(args["filter_name"]))
        return True
    if action == "edit":
        from aklog.cli.filter_editor import run_filter_edit_wizard

        config = load_config()
        name = args.get("filter_name") or config.filter.active
        profile = config.filter.profiles.get(name, FilterProfile())
        state = FilterState.from_filter_profile(profile, name, "")
        updated = run_filter_edit_wizard(name, state, profile.platform)
        if updated is None:
            return True
        profile.platform = updated.platform
        profile.package_mode = updated.package_mode
        profile.package = list(updated.package)
        profile.tag = list(updated.tag)
        profile.tag_exact = updated.tag_exact
        profile.tag_exclude = list(updated.tag_exclude)
        profile.tag_exclude_exact = list(updated.tag_exclude_exact)
        profile.msg = list(updated.msg)
        profile.msg_exact = updated.msg_exact
        profile.msg_exclude = list(updated.msg_exclude)
        profile.msg_exclude_exact = list(updated.msg_exclude_exact)
        config.filter.profiles[name] = profile
        save_config(config)
        console.print("Saved profile: {0}".format(name))
        return True
    return False
