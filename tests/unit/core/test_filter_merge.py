from __future__ import annotations

from aklog.core.config import AklogConfig
from aklog.core.filter_config import FilterProfile
from aklog.core.filter_merge import detect_explicit_filter_flags, merge_into_args, resolve_effective_filter


class TestFilterMerge:
    def test_detect_explicit_flags(self):
        flags = detect_explicit_filter_flags(["aklog", "-p", "com.foo", "-t", "Tag"])
        assert "package" in flags
        assert "tag" in flags

    def test_platform_override_merge(self):
        profile = FilterProfile(package_mode="top", tag=["Base"])
        from aklog.core.filter_config import PlatformFilterOverride

        profile.platform_overrides["android"] = PlatformFilterOverride(tag=["AndroidOnly"])
        effective = resolve_effective_filter(profile, "android")
        assert effective.tag == ["AndroidOnly"]
        assert effective.package_mode == "top"

    def test_merge_into_args_package_from_config(self):
        config = AklogConfig()
        config.filter.profiles["default"] = FilterProfile(package_mode="target", package=["com.app"])
        args = {
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
        merged = merge_into_args(args, config, "android", set())
        assert merged["package"] == ["com.app"]

    def test_cli_explicit_overrides_config(self):
        config = AklogConfig()
        config.filter.profiles["default"] = FilterProfile(package_mode="target", package=["com.app"])
        args = {
            "package": ["com.other"],
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
        merged = merge_into_args(args, config, "android", {"package"})
        assert merged["package"] == ["com.other"]
