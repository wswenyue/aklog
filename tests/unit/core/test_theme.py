from __future__ import annotations

from aklog.core.config import ColorConfig, LevelColors
from aklog.log.info import LogLevelHelper
from aklog.log.theme import LogColorTheme


class TestLogColorTheme:
    def test_default_styles_for_debug(self):
        theme = LogColorTheme()
        assert theme.msg_style(LogLevelHelper.DEBUG).color.name == "green"
        tag_style = theme.tag_style(LogLevelHelper.DEBUG)
        assert tag_style.color.name == "bright_green"
        assert tag_style.bold is True
        assert tag_style.underline is True
        assert not tag_style.reverse
        assert theme.level_style(LogLevelHelper.DEBUG).underline is True

    def test_custom_config_styles(self):
        colors = ColorConfig(
            meta="cyan",
            debug=LevelColors(base="magenta", tag="bright_magenta"),
        )
        theme = LogColorTheme(colors)
        assert theme.meta_style().color.name == "cyan"
        assert theme.msg_style(LogLevelHelper.DEBUG).color.name == "magenta"
        assert theme.tag_style(LogLevelHelper.DEBUG).color.name == "bright_magenta"

    def test_unknown_level_uses_verbose_colors(self):
        theme = LogColorTheme()
        assert theme.msg_style(LogLevelHelper.UNKNOWN).color.name == theme.config.verbose.base
