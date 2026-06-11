from __future__ import annotations

import pytest

from aklog.core.filter_config import (
    FilterConfig,
    FilterProfile,
    PlatformFilterOverride,
    default_filter_config,
    filter_config_to_toml_dict,
    parse_filter_config,
    profile_to_toml_table,
    validate_package_mode,
    validate_platform_pref,
    validate_profile_name,
)


class TestFilterConfig:
    def test_validate_package_mode(self):
        assert validate_package_mode("TOP") == "top"
        with pytest.raises(ValueError):
            validate_package_mode("invalid")

    def test_validate_platform_pref(self):
        assert validate_platform_pref("") == ""
        assert validate_platform_pref("Android") == "android"
        with pytest.raises(ValueError):
            validate_platform_pref("ios")

    def test_validate_profile_name(self):
        assert validate_profile_name("work") == "work"
        with pytest.raises(ValueError):
            validate_profile_name("")
        with pytest.raises(ValueError):
            validate_profile_name("android")

    def test_parse_filter_config_defaults(self):
        config = parse_filter_config({})
        assert config.active == "default"
        assert "default" in config.profiles

    def test_parse_filter_config_with_profiles(self):
        config = parse_filter_config(
            {
                "filter": {
                    "active": "work",
                    "profiles": {
                        "work": {"package_mode": "all", "tag": ["Net"]},
                        "android": {"tag": ["skip"]},
                    },
                }
            }
        )
        assert config.active == "work"
        assert config.profiles["work"].package_mode == "all"
        assert "android" not in config.profiles

    def test_parse_filter_config_with_platform_override(self):
        config = parse_filter_config(
            {
                "filter": {
                    "profiles": {
                        "default": {
                            "tag": ["Base"],
                            "android": {"package_mode": "target", "package": ["com.foo"]},
                        }
                    }
                }
            }
        )
        override = config.profiles["default"].platform_overrides["android"]
        assert override.package == ["com.foo"]

    def test_ensure_default_profile(self):
        config = FilterConfig(active="missing", profiles={"work": FilterProfile()})
        config.ensure_default_profile()
        assert config.active == "work"

    def test_profile_to_toml_roundtrip(self):
        profile = FilterProfile(package_mode="target", package=["com.foo"], tag_exact=True)
        profile.platform_overrides["android"] = PlatformFilterOverride(tag=["Net"])
        table = profile_to_toml_table(profile)
        assert table["package"] == ["com.foo"]
        assert table["android"]["tag"] == ["Net"]
        toml_dict = filter_config_to_toml_dict(default_filter_config())
        assert toml_dict["active"] == "default"
