from __future__ import annotations

from aklog.core.color_print import Colors, ColorStr, ColorStrArr, SimpleColorStr


class TestColorPrint:
    def test_color_str_render(self):
        text = ColorStr("hello", Colors.Green)
        rendered = str(text)
        assert "hello" in rendered

    def test_color_str_arr_join(self):
        arr = ColorStrArr(Colors.Blue)
        arr.add(SimpleColorStr("time", Colors.Gray))
        arr.add(ColorStr("INFO", Colors.LightBlue))
        rendered = str(arr)
        assert "time" in rendered
        assert "INFO" in rendered

    def test_copy_style(self):
        copied = Colors.RED.copy()
        assert copied.fg == Colors.RED.fg
