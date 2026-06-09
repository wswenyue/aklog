from __future__ import annotations

from aklog.core import config as config_module


class TestConfig:
    def test_default_color_config(self):
        colors = config_module.default_color_config()
        assert colors.meta == "grey50"
        assert colors.debug.base == "dark_sea_green2"
        assert colors.debug.tag == "spring_green2"
        assert colors.error.base == "indian_red"
        assert colors.error.tag == "bright_red"

    def test_load_config_missing_file(self, monkeypatch, tmp_path):
        monkeypatch.setattr(config_module, "config_path", lambda: str(tmp_path / "missing.toml"))
        loaded = config_module.load_config()
        assert loaded.colors.meta == "grey50"

    def test_load_config_from_toml(self, monkeypatch, tmp_path):
        path = tmp_path / "config.toml"
        path.write_text(
            """
[colors]
meta = "cyan"

[colors.error]
base = "magenta"
tag = "bright_magenta"
""".strip(),
            encoding="utf-8",
        )
        monkeypatch.setattr(config_module, "config_path", lambda: str(path))
        loaded = config_module.load_config()
        assert loaded.colors.meta == "cyan"
        assert loaded.colors.error.base == "magenta"
        assert loaded.colors.error.tag == "bright_magenta"

    def test_load_config_invalid_color_falls_back(self, monkeypatch, tmp_path):
        path = tmp_path / "config.toml"
        path.write_text('[colors]\nmeta = "not-a-real-color"\n', encoding="utf-8")
        monkeypatch.setattr(config_module, "config_path", lambda: str(path))
        loaded = config_module.load_config()
        assert loaded.colors.meta == "grey50"

    def test_init_config_file(self, monkeypatch, tmp_path):
        path = tmp_path / "config.toml"
        monkeypatch.setattr(config_module, "config_path", lambda: str(path))
        created_path, created = config_module.init_config_file()
        assert created is True
        assert created_path == str(path)
        assert path.is_file()
        assert "[colors]" in path.read_text(encoding="utf-8")

    def test_init_config_file_skips_existing(self, monkeypatch, tmp_path):
        path = tmp_path / "config.toml"
        path.write_text("existing", encoding="utf-8")
        monkeypatch.setattr(config_module, "config_path", lambda: str(path))
        _, created = config_module.init_config_file()
        assert created is False
        assert path.read_text(encoding="utf-8") == "existing"

    def test_init_config_file_force_overwrites(self, monkeypatch, tmp_path):
        path = tmp_path / "config.toml"
        path.write_text("existing", encoding="utf-8")
        monkeypatch.setattr(config_module, "config_path", lambda: str(path))
        _, created = config_module.init_config_file(force=True)
        assert created is True
        assert "[colors]" in path.read_text(encoding="utf-8")

    def test_config_dir_uses_xdg(self, monkeypatch, tmp_path):
        monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
        assert config_module.config_dir() == str(tmp_path / "aklog")
