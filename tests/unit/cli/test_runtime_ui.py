from __future__ import annotations

import pytest

from aklog.cli.runtime_ui import RuntimeContext, RuntimeMode, _is_interactive_enabled, _parse_command
from aklog.core.config import AklogConfig, save_config
from aklog.log.filter_state import FilterState


@pytest.fixture
def runtime_ctx(monkeypatch, tmp_path):
    path = tmp_path / "config.toml"
    monkeypatch.setattr("aklog.core.config.config_path", lambda: str(path))
    save_config(AklogConfig())
    state = FilterState(profile_name="default")
    return RuntimeContext("android:device1", "android", state)


class TestRuntimeUi:
    def test_status_text(self, runtime_ctx):
        text = runtime_ctx.status_text()
        assert "STREAM" in text
        assert "android:device1" in text

    def test_is_interactive_disabled(self):
        assert _is_interactive_enabled(True) is False

    def test_parse_command_empty(self, runtime_ctx):
        assert _parse_command("", runtime_ctx) is False

    def test_parse_command_tag_and_msg(self, runtime_ctx):
        assert _parse_command(":tag Net", runtime_ctx) is True
        assert runtime_ctx.filter_state.tag == ["Net"]
        assert _parse_command("msg Error", runtime_ctx) is True
        assert runtime_ctx.filter_state.msg == ["Error"]

    def test_parse_command_pkg_modes(self, runtime_ctx):
        _parse_command("pkg top", runtime_ctx)
        assert runtime_ctx.filter_state.package_mode == "top"
        _parse_command("pkg com.example", runtime_ctx)
        assert runtime_ctx.filter_state.package == ["com.example"]

    def test_parse_command_profile(self, runtime_ctx, monkeypatch, tmp_path):
        path = tmp_path / "config.toml"
        config = AklogConfig()
        from aklog.core.filter_config import FilterProfile

        config.filter.profiles["work"] = FilterProfile(tag=["Api"])
        save_config(config)
        monkeypatch.setattr("aklog.core.config.config_path", lambda: str(path))
        assert _parse_command("profile work", runtime_ctx) is True
        assert runtime_ctx.filter_state.profile_name == "work"

    def test_parse_command_unknown(self, runtime_ctx, capsys):
        from aklog.core import console as console_module

        monkeypatch = pytest.MonkeyPatch()
        monkeypatch.setattr(console_module, "print_error", lambda msg: print(msg))
        assert _parse_command("nope", runtime_ctx) is True
        monkeypatch.undo()

    def test_parse_command_quit(self, runtime_ctx):
        with pytest.raises(SystemExit):
            _parse_command("quit", runtime_ctx)

    def test_runtime_mode_enum(self):
        assert RuntimeMode.STREAM.value == "STREAM"
