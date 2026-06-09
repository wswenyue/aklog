from __future__ import annotations

from aklog.core.config import ColorConfig, LevelColors
from aklog.log.info import LogLevelHelper
from aklog.log.theme import LogColorTheme


class TestLogColorTheme:
    def test_default_styles_for_debug(self):
        theme = LogColorTheme()
        msg_style = theme.msg_style(LogLevelHelper.DEBUG)
        assert msg_style.color.name == "aquamarine1"
        assert msg_style.bold is True
        assert not msg_style.reverse
        tag_style = theme.tag_style(LogLevelHelper.DEBUG)
        assert tag_style.color.name == "dark_sea_green3"
        assert tag_style.bold is True
        assert tag_style.underline is True
        assert not tag_style.reverse
        level_style = theme.level_style(LogLevelHelper.DEBUG)
        assert level_style.color.name == "aquamarine1"
        assert level_style.bold is True
        assert not level_style.underline

    def test_custom_config_styles(self):
        colors = ColorConfig(
            meta="cyan",
            debug=LevelColors(base="magenta", tag="bright_magenta"),
        )
        theme = LogColorTheme(colors)
        assert theme.meta_style().color.name == "cyan"
        assert theme.msg_style(LogLevelHelper.DEBUG).color.name == "bright_magenta"
        assert theme.tag_style(LogLevelHelper.DEBUG).color.name == "magenta"

    def test_unknown_level_uses_verbose_colors(self):
        theme = LogColorTheme()
        assert theme.msg_style(LogLevelHelper.UNKNOWN).color.name == theme.config.verbose.tag
