from __future__ import annotations

import os
from unittest.mock import MagicMock, patch

from aklog.core import cmd_runner, comm_tools


class TestCmdRunnerExtended:
    def test_run_success(self):
        with patch("aklog.core.cmd_runner.subprocess.run") as mock_run:
            cmd_runner.run(["echo", "ok"], check=True)
            mock_run.assert_called_once()

    def test_popen_returns_process(self):
        proc = MagicMock()
        with patch("aklog.core.cmd_runner.subprocess.Popen", return_value=proc):
            assert cmd_runner.popen(["echo"]) is proc

    def test_run_shell(self):
        with patch("aklog.core.cmd_runner.subprocess.run") as mock_run:
            cmd_runner.run_shell("echo ok")
            mock_run.assert_called_once()
            assert mock_run.call_args.kwargs.get("shell") is True


class TestCommToolsExtended:
    def test_create_dir_not_exists(self, tmp_path):
        target = tmp_path / "a" / "b" / "c"
        comm_tools.create_dir_not_exists(str(target / "file.txt"))
        assert target.is_dir()

    def test_is_not_empty(self):
        assert comm_tools.is_not_empty("x") is True

    def test_read_file_lines(self, tmp_path):
        path = tmp_path / "data.txt"
        path.write_text("line1\nline2\n", encoding="utf-8")
        lines = comm_tools.read_file_lines(str(path))
        assert len(lines) == 2

    def test_read_file_line_iter(self, tmp_path):
        path = tmp_path / "data.txt"
        path.write_text("a\nb\n", encoding="utf-8")
        assert list(comm_tools.read_file_line_iter(str(path))) == ["a\n", "b\n"]

    def test_remove_file(self, tmp_path):
        path = tmp_path / "remove-me.txt"
        path.write_text("x", encoding="utf-8")
        comm_tools.remove_file(str(path))
        assert not path.exists()

    def test_get_path_helpers(self, tmp_path):
        path = str(tmp_path / "dir" / "file.txt")
        assert comm_tools.get_path_file_name(path) == "file.txt"
        assert comm_tools.get_path_dir(path).endswith("dir" + os.sep)

    def test_find_file_returns_first_match(self, tmp_path):
        nested = tmp_path / "sdk" / "default" / "openharmony" / "toolchains"
        nested.mkdir(parents=True)
        tool = nested / "hdc"
        tool.write_text("bin", encoding="utf-8")
        found = comm_tools.find_file("/sdk/*/openharmony/toolchains/hdc", str(tmp_path))
        assert found is not None
        assert found.endswith("hdc")

    def test_write_to_file_add(self, tmp_path):
        path = tmp_path / "log.txt"
        comm_tools.write_to_file("a", str(path))
        comm_tools.write_to_file_add("b", str(path))
        assert path.read_text(encoding="utf-8") == "ab"

    def test_find_files(self, tmp_path):
        nested = tmp_path / "sdk" / "default" / "openharmony" / "toolchains"
        nested.mkdir(parents=True)
        tool = nested / "hdc"
        tool.write_text("bin", encoding="utf-8")
        matches = comm_tools.find_files("/sdk/*/openharmony/toolchains/hdc", str(tmp_path))
        assert any(str(tool) == m or m.endswith("hdc") for m in matches)

    def test_platform_helpers(self, monkeypatch):
        monkeypatch.setattr("aklog.core.comm_tools.platform.system", lambda: "Darwin")
        assert comm_tools.is_mac_os() is True
        assert comm_tools.is_windows_os() is False
        assert comm_tools.is_py3() is True
        assert comm_tools.get_user_home_dir()
