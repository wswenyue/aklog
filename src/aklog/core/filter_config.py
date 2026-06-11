#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

import copy
from dataclasses import dataclass, field
from typing import Any, Dict, List

PACKAGE_MODES = ("top", "all", "target", "exclude")
PLATFORM_OVERRIDE_KEYS = ("android", "harmony")
RESERVED_PROFILE_NAMES = frozenset({"android", "harmony"})
FILTER_FIELD_KEYS = (
    "platform",
    "package_mode",
    "package",
    "tag",
    "tag_exact",
    "tag_exclude",
    "tag_exclude_exact",
    "msg",
    "msg_exact",
    "msg_exclude",
    "msg_exclude_exact",
)


@dataclass
class PlatformFilterOverride:
    package_mode: str | None = None
    package: List[str] = field(default_factory=list)
    tag: List[str] = field(default_factory=list)
    tag_exact: bool | None = None
    tag_exclude: List[str] = field(default_factory=list)
    tag_exclude_exact: List[str] = field(default_factory=list)
    msg: List[str] = field(default_factory=list)
    msg_exact: bool | None = None
    msg_exclude: List[str] = field(default_factory=list)
    msg_exclude_exact: List[str] = field(default_factory=list)

    def is_empty(self) -> bool:
        return (
            self.package_mode is None
            and not self.package
            and not self.tag
            and self.tag_exact is None
            and not self.tag_exclude
            and not self.tag_exclude_exact
            and not self.msg
            and self.msg_exact is None
            and not self.msg_exclude
            and not self.msg_exclude_exact
        )


@dataclass
class FilterProfile:
    platform: str = ""
    package_mode: str = "top"
    package: List[str] = field(default_factory=list)
    tag: List[str] = field(default_factory=list)
    tag_exact: bool = False
    tag_exclude: List[str] = field(default_factory=list)
    tag_exclude_exact: List[str] = field(default_factory=list)
    msg: List[str] = field(default_factory=list)
    msg_exact: bool = False
    msg_exclude: List[str] = field(default_factory=list)
    msg_exclude_exact: List[str] = field(default_factory=list)
    platform_overrides: Dict[str, PlatformFilterOverride] = field(default_factory=dict)

    def copy(self) -> FilterProfile:
        return copy.deepcopy(self)


@dataclass
class FilterConfig:
    active: str = "default"
    profiles: Dict[str, FilterProfile] = field(default_factory=dict)

    def ensure_default_profile(self) -> None:
        if not self.profiles:
            self.profiles["default"] = FilterProfile()
        if self.active not in self.profiles:
            if "default" in self.profiles:
                self.active = "default"
            else:
                self.active = next(iter(self.profiles))


def default_filter_config() -> FilterConfig:
    return FilterConfig(active="default", profiles={"default": FilterProfile()})


def _parse_str_list(value: Any) -> List[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(v) for v in value]
    return [str(value)]


def _parse_bool(value: Any, default: bool = False) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in ("true", "1", "yes"):
            return True
        if lowered in ("false", "0", "no"):
            return False
    return bool(value)


def _parse_override_section(data: Dict[str, Any]) -> PlatformFilterOverride:
    override = PlatformFilterOverride()
    if "package_mode" in data:
        override.package_mode = str(data["package_mode"])
    if "package" in data:
        override.package = _parse_str_list(data["package"])
    if "tag" in data:
        override.tag = _parse_str_list(data["tag"])
    if "tag_exact" in data:
        override.tag_exact = _parse_bool(data["tag_exact"])
    if "tag_exclude" in data:
        override.tag_exclude = _parse_str_list(data["tag_exclude"])
    if "tag_exclude_exact" in data:
        override.tag_exclude_exact = _parse_str_list(data["tag_exclude_exact"])
    if "msg" in data:
        override.msg = _parse_str_list(data["msg"])
    if "msg_exact" in data:
        override.msg_exact = _parse_bool(data["msg_exact"])
    if "msg_exclude" in data:
        override.msg_exclude = _parse_str_list(data["msg_exclude"])
    if "msg_exclude_exact" in data:
        override.msg_exclude_exact = _parse_str_list(data["msg_exclude_exact"])
    return override


def _parse_profile_section(data: Dict[str, Any]) -> FilterProfile:
    profile = FilterProfile()
    if "platform" in data:
        profile.platform = str(data.get("platform") or "")
    if "package_mode" in data:
        profile.package_mode = str(data["package_mode"])
    if "package" in data:
        profile.package = _parse_str_list(data["package"])
    if "tag" in data:
        profile.tag = _parse_str_list(data["tag"])
    if "tag_exact" in data:
        profile.tag_exact = _parse_bool(data["tag_exact"])
    if "tag_exclude" in data:
        profile.tag_exclude = _parse_str_list(data["tag_exclude"])
    if "tag_exclude_exact" in data:
        profile.tag_exclude_exact = _parse_str_list(data["tag_exclude_exact"])
    if "msg" in data:
        profile.msg = _parse_str_list(data["msg"])
    if "msg_exact" in data:
        profile.msg_exact = _parse_bool(data["msg_exact"])
    if "msg_exclude" in data:
        profile.msg_exclude = _parse_str_list(data["msg_exclude"])
    if "msg_exclude_exact" in data:
        profile.msg_exclude_exact = _parse_str_list(data["msg_exclude_exact"])
    for key in PLATFORM_OVERRIDE_KEYS:
        sub = data.get(key)
        if isinstance(sub, dict):
            override = _parse_override_section(sub)
            if not override.is_empty():
                profile.platform_overrides[key] = override
    return profile


def parse_filter_config(data: Dict[str, Any]) -> FilterConfig:
    filter_data = data.get("filter")
    if not isinstance(filter_data, dict):
        return default_filter_config()
    active = str(filter_data.get("active") or "default")
    profiles_data = filter_data.get("profiles")
    profiles: Dict[str, FilterProfile] = {}
    if isinstance(profiles_data, dict):
        for name, section in profiles_data.items():
            if name in RESERVED_PROFILE_NAMES:
                continue
            if isinstance(section, dict):
                profiles[str(name)] = _parse_profile_section(section)
    if not profiles:
        profiles["default"] = FilterProfile()
    if active not in profiles:
        active = "default" if "default" in profiles else next(iter(profiles))
    return FilterConfig(active=active, profiles=profiles)


def validate_package_mode(mode: str) -> str:
    lowered = mode.strip().lower()
    if lowered not in PACKAGE_MODES:
        raise ValueError("package_mode must be one of: {0}".format(", ".join(PACKAGE_MODES)))
    return lowered


def validate_platform_pref(platform: str) -> str:
    lowered = (platform or "").strip().lower()
    if lowered not in ("", "android", "harmony"):
        raise ValueError("platform must be empty, android, or harmony")
    return lowered


def validate_profile_name(name: str) -> str:
    if not name or not name.strip():
        raise ValueError("profile name cannot be empty")
    if name in RESERVED_PROFILE_NAMES:
        raise ValueError('profile name "{0}" is reserved'.format(name))
    return name


def profile_to_toml_table(profile: FilterProfile) -> Dict[str, Any]:
    table: Dict[str, Any] = {
        "platform": profile.platform,
        "package_mode": profile.package_mode,
        "package": list(profile.package),
        "tag": list(profile.tag),
        "tag_exact": profile.tag_exact,
        "tag_exclude": list(profile.tag_exclude),
        "tag_exclude_exact": list(profile.tag_exclude_exact),
        "msg": list(profile.msg),
        "msg_exact": profile.msg_exact,
        "msg_exclude": list(profile.msg_exclude),
        "msg_exclude_exact": list(profile.msg_exclude_exact),
    }
    for key, override in profile.platform_overrides.items():
        if override.is_empty():
            continue
        sub: Dict[str, Any] = {}
        if override.package_mode is not None:
            sub["package_mode"] = override.package_mode
        if override.package:
            sub["package"] = list(override.package)
        if override.tag:
            sub["tag"] = list(override.tag)
        if override.tag_exact is not None:
            sub["tag_exact"] = override.tag_exact
        if override.tag_exclude:
            sub["tag_exclude"] = list(override.tag_exclude)
        if override.tag_exclude_exact:
            sub["tag_exclude_exact"] = list(override.tag_exclude_exact)
        if override.msg:
            sub["msg"] = list(override.msg)
        if override.msg_exact is not None:
            sub["msg_exact"] = override.msg_exact
        if override.msg_exclude:
            sub["msg_exclude"] = list(override.msg_exclude)
        if override.msg_exclude_exact:
            sub["msg_exclude_exact"] = list(override.msg_exclude_exact)
        table[key] = sub
    return table


def filter_config_to_toml_dict(config: FilterConfig) -> Dict[str, Any]:
    config.ensure_default_profile()
    profiles: Dict[str, Any] = {}
    for name, profile in config.profiles.items():
        profiles[name] = profile_to_toml_table(profile)
    return {"active": config.active, "profiles": profiles}
