from __future__ import annotations

from aklog.cli.runtime_help import build_help_panel, print_runtime_help_text
from aklog.log.filter_state import FilterState


class TestRuntimeHelp:
    def test_build_help_panel_contains_filter_summary(self):
        state = FilterState(profile_name="default", package_mode="top")
        panel = build_help_panel("android:emu", state, "STREAM")
        assert panel.title == "aklog 运行期帮助"
        assert "default" in state.summary()

    def test_print_runtime_help_text(self, capsys):
        print_runtime_help_text()
        out = capsys.readouterr().out
        assert "F1" in out
        assert ":w" in out
