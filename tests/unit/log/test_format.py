from __future__ import annotations

from aklog.log.format import JsonValueFormat


class TestJsonValueFormat:
    def test_extracts_json_key_value(self):
        fmt = JsonValueFormat(_keys=["userId"])
        out = fmt.format_content('{"userId":"12345","name":"demo"}')
        assert out is not None
        assert "userId" in out
        assert "12345" in out

    def test_returns_none_when_key_missing(self):
        fmt = JsonValueFormat(_keys=["missing"])
        assert fmt.format_content('{"userId":"1"}') is None

    def test_returns_none_for_empty_input(self):
        fmt = JsonValueFormat(_keys=["userId"])
        assert fmt.format_content("") is None

    def test_multiple_keys(self):
        fmt = JsonValueFormat(_keys=["a", "b"])
        out = fmt.format_content('{"a":"1","b":"2"}')
        assert out is not None
        assert "'a'" in out
        assert "'b'" in out
