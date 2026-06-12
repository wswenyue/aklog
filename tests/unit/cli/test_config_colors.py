from __future__ import annotations

import pytest

from aklog.cli import config_colors
from aklog.core.config import AklogConfig, save_config


@pytest.fixture
def config_file(monkeypatch, tmp_path):
    path = tmp_path / "config.toml"
    monkeypatch.setattr("aklog.core.config.config_path", lambda: str(path))
    save_config(AklogConfig())
    return path


class TestConfigColors:
    def test_text_block(self):
        block = config_colors.Text_block("cyan")
        assert block.plain == "████"
        assert str(block.style) == "cyan"

    def test_colors_get_and_set(self, config_file, capsys):
        config_colors.colors_set("meta", "cyan")
        config_colors.colors_get("meta")
        assert "cyan" in capsys.readouterr().out

    def test_colors_set_unknown_key(self, config_file):
        with pytest.raises(ValueError):
            config_colors.colors_set("unknown.field", "red")

    def test_colors_reset(self, config_file):
        config_colors.colors_set("meta", "cyan")
        config_colors.colors_reset()

    def test_run_colors_command_actions(self, config_file, monkeypatch):
        monkeypatch.setattr(config_colors, "_is_tty", lambda: False)
        assert config_colors.run_colors_command("get", {"color_key": "meta"}) is True
        assert config_colors.run_colors_command("set", {"color_key": "meta", "color_value": "blue"}) is True
        assert config_colors.run_colors_command("show", {}) is True
        assert config_colors.run_colors_command("reset", {}) is True
        assert config_colors.run_colors_command("edit", {}) is True
        assert config_colors.run_colors_command("unknown", {}) is False
