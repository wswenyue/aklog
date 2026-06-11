from __future__ import annotations

import pytest

from aklog.cli.config_filter import filter_get, filter_set, parse_filter_path
from aklog.core.config import AklogConfig, save_config


class TestConfigFilter:
    def test_parse_filter_path(self):
        path = parse_filter_path("default.android.package")
        assert path.profile == "default"
        assert path.platform == "android"
        assert path.key == "package"

    def test_filter_set_and_get(self, monkeypatch, tmp_path):
        path = tmp_path / "config.toml"
        monkeypatch.setattr("aklog.core.config.config_path", lambda: str(path))
        save_config(AklogConfig())
        filter_set("default.tag", "Network,Http")
        assert filter_get("default.tag") == "Network,Http"

    def test_reserved_profile_name(self):
        with pytest.raises(ValueError):
            parse_filter_path("android.package")
