from __future__ import annotations

from aklog.core.color_presets import (
    COLOR_FIELDS,
    PRESETS,
    get_color_field,
    high_contrast_preset,
    mono_preset,
    set_color_field,
    soft_preset,
)
from aklog.core.config import ColorConfig, default_color_config


class TestColorPresets:
    def test_presets_return_color_config(self):
        assert isinstance(PRESETS["default"](), ColorConfig)
        assert isinstance(high_contrast_preset(), ColorConfig)
        assert isinstance(soft_preset(), ColorConfig)
        assert isinstance(mono_preset(), ColorConfig)

    def test_get_and_set_top_level_field(self):
        config = default_color_config()
        assert get_color_field(config, "meta") == "grey50"
        set_color_field(config, "meta", "cyan")
        assert config.meta == "cyan"

    def test_get_and_set_level_field(self):
        config = default_color_config()
        assert get_color_field(config, "debug.base") == "dark_sea_green3"
        set_color_field(config, "debug.tag", "bright_green")
        assert config.debug.tag == "bright_green"

    def test_color_fields_cover_levels(self):
        for key in COLOR_FIELDS:
            if "." in key:
                assert get_color_field(default_color_config(), key)
