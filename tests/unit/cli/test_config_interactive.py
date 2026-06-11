from __future__ import annotations

from aklog.cli.config_interactive import run_config_console
from aklog.core.config import AklogConfig, save_config


class TestConfigInteractive:
    def test_non_tty_shows_config(self, monkeypatch, tmp_path, capsys):
        path = tmp_path / "config.toml"
        monkeypatch.setattr("aklog.core.config.config_path", lambda: str(path))
        save_config(AklogConfig())
        monkeypatch.setattr("aklog.cli.config_interactive._is_tty", lambda: False)
        run_config_console()
        out = capsys.readouterr().out
        assert str(path) in out or "Config path" in out
