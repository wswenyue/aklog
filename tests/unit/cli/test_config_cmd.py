from __future__ import annotations

from aklog.cli.config_cmd import run_config_command


class TestConfigCmd:
    def test_config_path(self, monkeypatch, tmp_path, capsys):
        path = tmp_path / "config.toml"
        monkeypatch.setattr("aklog.cli.config_cmd.config_path", lambda: str(path))
        assert run_config_command({"config_action": "path"}) is True
        assert str(path) in capsys.readouterr().out

    def test_config_init(self, monkeypatch, tmp_path, capsys):
        path = tmp_path / "config.toml"
        monkeypatch.setattr("aklog.core.config.config_path", lambda: str(path))
        assert run_config_command({"config_action": "init"}) is True
        assert "Created" in capsys.readouterr().out

    def test_config_migrate(self, monkeypatch, tmp_path, capsys):
        path = tmp_path / "config.toml"
        path.write_text("[colors]\nmeta = 'grey50'\n", encoding="utf-8")
        monkeypatch.setattr("aklog.cli.config_cmd.config_path", lambda: str(path))
        monkeypatch.setattr("aklog.core.config.config_path", lambda: str(path))
        assert run_config_command({"config_action": "migrate"}) is True

    def test_filter_without_subcommand(self, capsys):
        assert run_config_command({"config_action": "filter"}) is True
        assert "Usage" in capsys.readouterr().out

    def test_colors_subcommand(self, monkeypatch, tmp_path):
        path = tmp_path / "config.toml"
        monkeypatch.setattr("aklog.core.config.config_path", lambda: str(path))
        from aklog.core.config import AklogConfig, save_config

        save_config(AklogConfig())
        monkeypatch.setattr("aklog.cli.config_colors._is_tty", lambda: False)
        assert run_config_command({"config_action": "colors", "colors_action": "show"}) is True

    def test_unknown_action(self, capsys):
        assert run_config_command({"config_action": "nope"}) is True
        assert "Unknown" in capsys.readouterr().out
