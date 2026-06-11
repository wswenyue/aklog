#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

import copy
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from aklog.core.filter_config import FilterProfile, PlatformFilterOverride
from aklog.core.filter_merge import effective_filter_to_args, resolve_effective_filter


@dataclass
class FilterState:
    profile_name: str = "default"
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
    level: Optional[str] = None
    dirty: bool = False

    def copy(self) -> FilterState:
        return copy.deepcopy(self)

    def to_filter_profile(self) -> FilterProfile:
        profile = FilterProfile(
            platform="",
            package_mode=self.package_mode,
            package=list(self.package),
            tag=list(self.tag),
            tag_exact=self.tag_exact,
            tag_exclude=list(self.tag_exclude),
            tag_exclude_exact=list(self.tag_exclude_exact),
            msg=list(self.msg),
            msg_exact=self.msg_exact,
            msg_exclude=list(self.msg_exclude),
            msg_exclude_exact=list(self.msg_exclude_exact),
        )
        return profile

    def to_args_dict(self) -> Dict:
        args = effective_filter_to_args(self.to_filter_profile())
        if self.level:
            args["level"] = [self.level]
        return args

    @classmethod
    def from_filter_profile(cls, profile: FilterProfile, profile_name: str, device_platform: str = "") -> FilterState:
        effective = resolve_effective_filter(profile, device_platform)
        return cls(
            profile_name=profile_name,
            platform=device_platform,
            package_mode=effective.package_mode,
            package=list(effective.package),
            tag=list(effective.tag),
            tag_exact=effective.tag_exact,
            tag_exclude=list(effective.tag_exclude),
            tag_exclude_exact=list(effective.tag_exclude_exact),
            msg=list(effective.msg),
            msg_exact=effective.msg_exact,
            msg_exclude=list(effective.msg_exclude),
            msg_exclude_exact=list(effective.msg_exclude_exact),
        )

    @classmethod
    def from_args_dict(cls, args: Dict, profile_name: str = "default", platform: str = "") -> FilterState:
        state = cls(profile_name=profile_name, platform=platform)
        if args.get("package"):
            state.package_mode = "target"
            state.package = list(args["package"])
        elif args.get("package_not"):
            state.package_mode = "exclude"
            state.package = list(args["package_not"])
        elif args.get("package_all"):
            state.package_mode = "all"
        elif args.get("package_current_top"):
            state.package_mode = "top"
        if args.get("tag"):
            state.tag = list(args["tag"])
            state.tag_exact = False
        if args.get("tag_exact"):
            state.tag = list(args["tag_exact"])
            state.tag_exact = True
        if args.get("tag_not"):
            state.tag_exclude = list(args["tag_not"])
        if args.get("tag_not_exact"):
            state.tag_exclude_exact = list(args["tag_not_exact"])
        if args.get("msg"):
            state.msg = list(args["msg"])
            state.msg_exact = False
        if args.get("msg_exact"):
            state.msg = list(args["msg_exact"])
            state.msg_exact = True
        if args.get("msg_not"):
            state.msg_exclude = list(args["msg_not"])
        if args.get("msg_not_exact"):
            state.msg_exclude_exact = list(args["msg_not_exact"])
        level = args.get("level")
        if level:
            if isinstance(level, list):
                state.level = str(level[0]) if level else None
            else:
                state.level = str(level)
        return state

    def summary(self) -> str:
        pkg = self.package_mode.upper()
        if self.package_mode in ("target", "exclude") and self.package:
            pkg = "{0}:{1}".format(pkg, ",".join(self.package))
        tag = ",".join(self.tag) if self.tag else "-"
        msg = ",".join(self.msg) if self.msg else "-"
        lvl = self.level or "-"
        profile = self.profile_name
        if self.dirty:
            profile = "{0}*".format(profile)
        return "profile:{0} | pkg:{1} | tag:{2} | msg:{3} | lvl:{4}".format(profile, pkg, tag, msg, lvl)

    def apply_to_platform_override(self, platform: str) -> PlatformFilterOverride:
        override = PlatformFilterOverride()
        override.package_mode = self.package_mode
        override.package = list(self.package)
        override.tag = list(self.tag)
        override.tag_exact = self.tag_exact
        override.tag_exclude = list(self.tag_exclude)
        override.tag_exclude_exact = list(self.tag_exclude_exact)
        override.msg = list(self.msg)
        override.msg_exact = self.msg_exact
        override.msg_exclude = list(self.msg_exclude)
        override.msg_exclude_exact = list(self.msg_exclude_exact)
        return override
