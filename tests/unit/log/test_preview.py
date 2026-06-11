from __future__ import annotations

from aklog.log.preview import render_log_preview
from aklog.log.theme import LogColorTheme


class TestPreview:
    def test_render_log_preview_returns_five_lines(self):
        lines = render_log_preview(LogColorTheme())
        assert len(lines) == 5
        assert all(line.plain for line in lines)
