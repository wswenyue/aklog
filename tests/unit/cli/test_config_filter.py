from __future__ import annotations

import pytest

from aklog.cli.config_filter import (
    filter_delete,
    filter_get,
    filter_list,
    filter_new,
    filter_set,
    filter_show,
    filter_unset,
    filter_use,
    load_filter_state_for_device,
    parse_filter_path,
    run_filter_command,
    save_filter_state_to_config,
)
from aklog.core.config import AklogConfig, save_config
from aklog.log.filter_state import FilterState


@pytest.fixture
def config_file(monkeypatch, tmp_path):
    path = tmp_path / "config.toml"
    monkeypatch.setattr("aklog.core.config.config_path", lambda: str(path))
    save_config(AklogConfig())
    return path


class TestConfigFilter:
    def test_parse_filter_path(self):
        path = parse_filter_path("default.android.package")
        assert path.profile == "default"
        assert path.platform == "android"
        assert path.key == "package"

    def test_parse_filter_path_profile_only(self):
        path = parse_filter_path("default")
        assert path.key is None

    def test_parse_filter_path_profile_key(self):
        path = parse_filter_path("default.tag")
        assert path.platform is None
        assert path.key == "tag"

    def test_parse_filter_path_platform_section(self):
        path = parse_filter_path("default.android")
        assert path.platform == "android"
        assert path.key is None

    def test_invalid_filter_path(self):
        with pytest.raises(ValueError):
            parse_filter_path("default.android.foo.bar")

    def test_reserved_profile_name(self):
        with pytest.raises(ValueError):
            parse_filter_path("android.package")

    def test_filter_set_and_get(self, config_file):
        filter_set("default.tag", "Network,Http")
        assert filter_get("default.tag") == "Network,Http"

    def test_filter_set_bool_and_list(self, config_file):
        filter_set("default.tag_exact", "true")
        assert filter_get("default.tag_exact") == "True"
        filter_set("default.package_mode", "all")
        assert filter_get("default.package_mode") == "all"

    def test_filter_set_platform_override(self, config_file):
        filter_set("work.android.package", "com.foo")
        assert filter_get("work.android.package") == "com.foo"

    def test_filter_get_profile_status(self, config_file):
        assert filter_get("default") == "present"
        assert filter_get("missing") == "missing"

    def test_filter_get_platform_section(self, config_file):
        assert filter_get("default.android") == "empty"
        filter_set("default.android.tag", "Net")
        assert filter_get("default.android") == "present"

    def test_filter_set_requires_key(self, config_file):
        with pytest.raises(ValueError):
            filter_set("default", "x")

    def test_filter_unset_fields(self, config_file):
        filter_set("default.tag", "A")
        filter_unset("default.tag")
        assert filter_get("default.tag") == ""

    def test_filter_unset_platform_section(self, config_file):
        filter_set("default.harmony.tag", "H")
        filter_unset("default.harmony")
        assert filter_get("default.harmony") == "empty"

    def test_filter_use_and_list(self, config_file):
        filter_new("work")
        filter_use("work")
        filter_list()

    def test_filter_show_missing_profile(self, config_file):
        filter_show("nope")

    def test_filter_show_with_override(self, config_file):
        filter_set("default.android.tag", "Api")
        filter_show("default")

    def test_filter_new_and_copy(self, config_file):
        filter_set("default.tag", "Base")
        filter_new("copy", copy_from="default")
        assert filter_get("copy.tag") == "Base"

    def test_filter_new_duplicate(self, config_file):
        with pytest.raises(ValueError):
            filter_new("default")

    def test_filter_delete(self, config_file):
        filter_new("temp")
        filter_delete("temp")

    def test_filter_delete_last_profile(self, config_file):
        with pytest.raises(ValueError):
            filter_delete("default")

    def test_save_and_load_filter_state(self, config_file):
        state = FilterState(profile_name="default", package_mode="all", tag=["Net"])
        save_filter_state_to_config(state, "android")
        loaded = load_filter_state_for_device("default", "android")
        assert loaded.package_mode == "all"

    def test_save_filter_state_global(self, config_file):
        state = FilterState(profile_name="default", tag=["Global"])
        save_filter_state_to_config(state, "")
        loaded = load_filter_state_for_device("default", "")
        assert loaded.tag == ["Global"]

    def test_run_filter_command(self, config_file, monkeypatch):
        monkeypatch.setattr("aklog.cli.filter_editor._is_tty", lambda: False)
        assert run_filter_command("list", {}) is True
        assert run_filter_command("show", {}) is True
        assert run_filter_command("get", {"filter_path": "default.package_mode"}) is True
        assert run_filter_command("set", {"filter_path": "default.tag", "filter_value": "X"}) is True
        assert run_filter_command("unset", {"filter_path": "default.tag"}) is True
        filter_new("cmdtest")
        assert run_filter_command("use", {"filter_name": "cmdtest"}) is True
        assert run_filter_command("new", {"filter_name": "cmdtest2", "copy_from": "cmdtest"}) is True
        assert run_filter_command("edit", {"filter_name": "default"}) is True
        assert run_filter_command("delete", {"filter_name": "cmdtest2"}) is True
        assert run_filter_command("unknown", {}) is False
