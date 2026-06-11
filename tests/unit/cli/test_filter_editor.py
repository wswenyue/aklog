from __future__ import annotations

from aklog.cli.filter_editor import (
    _comma_list,
    run_filter_edit_wizard,
    run_filter_field_editor,
    run_profile_platform_pref_editor,
)
from aklog.log.filter_state import FilterState


class TestFilterEditor:
    def test_comma_list(self):
        assert _comma_list("") == []
        assert _comma_list("a, b ,c") == ["a", "b", "c"]

    def test_non_tty_returns_unchanged(self, monkeypatch):
        monkeypatch.setattr("aklog.cli.filter_editor._is_tty", lambda: False)
        state = FilterState(tag=["Net"])
        assert run_filter_field_editor(state) is state
        assert run_profile_platform_pref_editor("android") == "android"
        assert run_filter_edit_wizard("default", state) is None
