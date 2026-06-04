from __future__ import annotations

import subprocess
from unittest.mock import MagicMock, patch

import pytest

from aklog.core import cmd_runner


class TestCmdRunner:
    def test_check_output_success(self):
        with patch("aklog.core.cmd_runner.subprocess.check_output", return_value=b"ok") as mock:
            assert cmd_runner.check_output(["echo", "ok"]) == "ok"
            mock.assert_called_once()

    def test_check_output_failure_py3(self):
        with patch(
            "aklog.core.cmd_runner.subprocess.check_output",
            side_effect=subprocess.CalledProcessError(1, ["bad"]),
        ):
            with pytest.raises(subprocess.CalledProcessError):
                cmd_runner.check_output(["bad"])

    def test_iter_lines(self):
        proc = MagicMock()
        proc.stdout.readline.side_effect = ["line1\n", "line2\n", ""]
        proc.wait.return_value = 0
        with patch("aklog.core.cmd_runner.popen", return_value=proc):
            lines = list(cmd_runner.iter_lines(["fake"]))
        assert lines == ["line1\n", "line2\n"]

    def test_iter_lines_closes_stdout(self):
        proc = MagicMock()
        proc.stdout.readline.side_effect = [""]
        proc.wait.return_value = 0
        with patch("aklog.core.cmd_runner.popen", return_value=proc):
            list(cmd_runner.iter_lines(["fake"]))
        proc.stdout.close.assert_called_once()

    def test_run_and_run_shell(self):
        with patch("aklog.core.cmd_runner.subprocess.run") as mock_run:
            cmd_runner.run(["true"], check=False)
            cmd_runner.run_shell("echo ok", check=False)
        assert mock_run.call_count == 2

    def test_popen_delegates(self):
        proc = MagicMock()
        with patch("aklog.core.cmd_runner.subprocess.Popen", return_value=proc):
            assert cmd_runner.popen(["echo"]) is proc

    def test_iter_lines_non_zero_exit(self):
        proc = MagicMock()
        proc.stdout.readline.side_effect = [""]
        proc.wait.return_value = 1
        with patch("aklog.core.cmd_runner.popen", return_value=proc):
            with pytest.raises(subprocess.CalledProcessError):
                list(cmd_runner.iter_lines(["fake"]))
