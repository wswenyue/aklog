#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import Optional

from aklog.core.filter_config import PACKAGE_MODES, PLATFORM_OVERRIDE_KEYS, validate_package_mode, validate_platform_pref
from aklog.log.filter_state import FilterState


def _is_tty() -> bool:
    import sys

    return sys.stdin.isatty() and sys.stdout.isatty()


def _comma_list(text: str) -> list:
    if not text or not text.strip():
        return []
    return [part.strip() for part in text.split(",") if part.strip()]


def run_filter_field_editor(state: FilterState, scope: str = "global") -> FilterState:
    """Interactive filter editor; scope is global, android, or harmony."""
    if not _is_tty():
        return state
    import questionary

    draft = state.copy()
    if scope in PLATFORM_OVERRIDE_KEYS:
        draft.platform = scope

    while True:
        action = questionary.select(
            "选择要编辑的过滤项",
            choices=[
                "package_mode / 包名策略",
                "package / 包名列表",
                "tag / 包含 Tag",
                "tag_exclude / 排除 Tag",
                "msg / 包含消息",
                "msg_exclude / 排除消息",
                "完成并应用",
                "取消",
            ],
        ).ask()
        if action is None or action == "取消":
            return state
        if action == "完成并应用":
            return draft
        if action.startswith("package_mode"):
            mode = questionary.select("包名策略", choices=list(PACKAGE_MODES)).ask()
            if mode:
                draft.package_mode = validate_package_mode(mode)
        elif action.startswith("package"):
            text = questionary.text("包名（逗号分隔）", default=",".join(draft.package)).ask()
            if text is not None:
                draft.package = _comma_list(text)
        elif action.startswith("tag /"):
            text = questionary.text("Tag 包含（逗号分隔）", default=",".join(draft.tag)).ask()
            if text is not None:
                draft.tag = _comma_list(text)
            exact = questionary.confirm("精确匹配 Tag？", default=draft.tag_exact).ask()
            if exact is not None:
                draft.tag_exact = exact
        elif action.startswith("tag_exclude"):
            text = questionary.text("Tag 排除（逗号分隔）", default=",".join(draft.tag_exclude)).ask()
            if text is not None:
                draft.tag_exclude = _comma_list(text)
        elif action.startswith("msg /"):
            text = questionary.text("消息包含（逗号分隔）", default=",".join(draft.msg)).ask()
            if text is not None:
                draft.msg = _comma_list(text)
            exact = questionary.confirm("精确匹配消息？", default=draft.msg_exact).ask()
            if exact is not None:
                draft.msg_exact = exact
        elif action.startswith("msg_exclude"):
            text = questionary.text("消息排除（逗号分隔）", default=",".join(draft.msg_exclude)).ask()
            if text is not None:
                draft.msg_exclude = _comma_list(text)


def run_profile_platform_pref_editor(current: str = "") -> str:
    if not _is_tty():
        return current
    import questionary

    choice = questionary.select(
        "设备平台偏好（启动时选设备）",
        choices=["不限", "android", "harmony"],
    ).ask()
    if choice is None:
        return current
    if choice == "不限":
        return ""
    return validate_platform_pref(choice)


def run_filter_edit_wizard(profile_name: str, state: FilterState, base_platform_pref: str = "") -> Optional[FilterState]:
    if not _is_tty():
        return None
    import questionary

    scope = questionary.select(
        "编辑范围",
        choices=["全局（基础段）", "仅 Android 覆盖", "仅 Harmony 覆盖"],
    ).ask()
    if scope is None:
        return None
    if scope.startswith("全局"):
        pref = run_profile_platform_pref_editor(base_platform_pref)
        draft = run_filter_field_editor(state, scope="global")
        draft.platform = pref
        return draft
    if scope.startswith("仅 Android"):
        return run_filter_field_editor(state, scope="android")
    return run_filter_field_editor(state, scope="harmony")
