from __future__ import annotations

import pytest

from aklog.core import comm_tools


class TestIsEmpty:
    def test_none_and_blank_string(self):
        assert comm_tools.is_empty(None) is True
        assert comm_tools.is_empty("") is True
        assert comm_tools.is_empty("None") is True
        assert comm_tools.is_empty("  ") is True

    def test_non_empty_values(self):
        assert comm_tools.is_empty("hello") is False
        assert comm_tools.is_empty([1]) is False
        assert comm_tools.is_empty({"a": 1}) is False

    def test_empty_list_and_dict(self):
        assert comm_tools.is_empty([]) is True
        assert comm_tools.is_empty({}) is True


class TestGetStr:
    def test_bytes_decoding(self):
        assert comm_tools.get_str(b"abc") == "abc"

    def test_other_types(self):
        assert comm_tools.get_str(123) == "123"


class TestToInt:
    def test_int_passthrough(self):
        assert comm_tools.to_int(7) == 7

    def test_string_conversion(self):
        assert comm_tools.to_int("42") == 42


class TestMatchStr:
    def test_exact_match(self):
        assert comm_tools.match_str("abc", "abc") is True
        assert comm_tools.match_str("abc", "abd") is False

    def test_fuzzy_match(self):
        assert comm_tools.match_str("ab", "xaby", is_exact=False) is True

    def test_ignore_case(self):
        assert comm_tools.match_str("Ab", "ab", is_ignore_case=True) is True


class TestPromptChoice:
    def test_returns_selected_index(self, monkeypatch):
        monkeypatch.setattr(comm_tools, "prompt_input", lambda _msg: "2")
        assert comm_tools.prompt_choice(["a", "b", "c"], title="pick") == 1

    def test_retries_on_invalid_input(self, monkeypatch):
        answers = iter(["0", "abc", "1"])
        monkeypatch.setattr(comm_tools, "prompt_input", lambda _msg: next(answers))
        assert comm_tools.prompt_choice(["dev1", "dev2"]) == 0

    def test_empty_options_raises(self):
        with pytest.raises(ValueError, match="no options"):
            comm_tools.prompt_choice([])


class TestFileHelpers:
    def test_write_and_read_file(self, tmp_path):
        target = tmp_path / "nested" / "out.txt"
        comm_tools.write_to_file_no_error("hello", str(target))
        assert target.read_text(encoding="utf-8") == "hello"

    def test_is_exe(self, tmp_path):
        script = tmp_path / "run.sh"
        script.write_text("#!/bin/sh\n", encoding="utf-8")
        script.chmod(0o755)
        assert comm_tools.is_exe(str(script)) is True
        assert comm_tools.is_exe(str(tmp_path / "missing")) is False
