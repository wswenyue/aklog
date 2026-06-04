from __future__ import annotations

from aklog.core import debug


class TestDebug:
    def test_log_print(self, capsys):
        debug.log("hello debug")
        captured = capsys.readouterr()
        assert "hello debug" in captured.out

    def test_log_err(self, capsys):
        debug.log_err("something failed")
        captured = capsys.readouterr()
        assert "something failed" in captured.out
        assert "Error Begin" in captured.out
