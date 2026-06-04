from __future__ import annotations

import subprocess
from unittest.mock import MagicMock, patch

import pytest

from aklog.device.hdc import HdcCmd, HdcHelper


@pytest.fixture(autouse=True)
def reset_hdc_cache():
    HdcCmd._hdc = None
    yield
    HdcCmd._hdc = None


class TestHdcCmd:
    def test_find_hdc_from_lib_dir(self, tmp_path, monkeypatch):
        hdc_bin = tmp_path / "hdc"
        hdc_bin.write_text("#!/bin/sh\n", encoding="utf-8")
        hdc_bin.chmod(0o755)
        monkeypatch.delenv("HARMONY_HOME", raising=False)
        monkeypatch.setattr("aklog.device.hdc.bundled_tool", lambda name: str(tmp_path / name))
        assert HdcCmd.find_hdc() == str(hdc_bin)

    def test_find_hdc_missing_returns_none(self, monkeypatch):
        monkeypatch.delenv("HARMONY_HOME", raising=False)
        monkeypatch.setattr(
            "aklog.device.hdc.bundled_tool",
            lambda name: f"/nonexistent/{name}",
        )
        assert HdcCmd.find_hdc() is None


class TestHdcHelper:
    def _make_helper(self, tmp_path, monkeypatch, device_id="target1"):
        hdc_bin = tmp_path / "hdc"
        hdc_bin.write_text("#!/bin/sh\n", encoding="utf-8")
        hdc_bin.chmod(0o755)
        monkeypatch.delenv("HARMONY_HOME", raising=False)
        monkeypatch.setattr("aklog.device.hdc.bundled_tool", lambda name: str(tmp_path / name))
        return HdcHelper(device_id=device_id)

    def test_list_connected_devices(self, tmp_path, monkeypatch):
        self._make_helper(tmp_path, monkeypatch)
        lines = ["target-a", "[Empty]", "target-b"]
        with patch("aklog.device.hdc.cmd_runner.iter_lines", return_value=iter(lines)):
            assert HdcHelper.list_connected_devices() == ["target-a", "target-b"]

    def test_check_connect_failure_raises(self, tmp_path, monkeypatch):
        helper = self._make_helper(tmp_path, monkeypatch, device_id="missing")
        with (
            patch.object(helper, "_HdcHelper__check_connect", return_value=False),
            patch.object(helper, "_HdcHelper__restart_connect"),
        ):
            with pytest.raises(ValueError, match='device "missing" not connected'):
                helper.check_connect()

    def test_unavailable_hdc_raises(self, monkeypatch):
        monkeypatch.delenv("HARMONY_HOME", raising=False)
        helper = HdcHelper(hdc_path="/nonexistent")
        with pytest.raises(OSError, match="hdc not found"):
            helper._base_argv()

    def test_target_argv_includes_target_flag(self, tmp_path, monkeypatch):
        helper = self._make_helper(tmp_path, monkeypatch, device_id="target-x")
        argv = helper._target_argv("shell ls")
        assert argv[:4] == [str(tmp_path / "hdc"), "-t", "target-x", "shell"]

    def test_check_connect_success(self, tmp_path, monkeypatch):
        helper = self._make_helper(tmp_path, monkeypatch, device_id="target-a")
        with patch("aklog.device.hdc.cmd_runner.iter_lines", return_value=iter(["target-a"])):
            assert helper._HdcHelper__check_connect() is True

    def test_check_connect_empty_targets(self, tmp_path, monkeypatch):
        helper = self._make_helper(tmp_path, monkeypatch)
        with patch("aklog.device.hdc.cmd_runner.iter_lines", return_value=iter(["[Empty]"])):
            assert helper._HdcHelper__check_connect() is False

    def test_check_connect_restarts_and_succeeds(self, tmp_path, monkeypatch):
        helper = self._make_helper(tmp_path, monkeypatch)
        with (
            patch.object(helper, "_HdcHelper__check_connect", side_effect=[False, True]),
            patch.object(helper, "_HdcHelper__restart_connect") as restart,
        ):
            helper.check_connect()
        restart.assert_called_once()

    def test_run_cmd_and_file_cmd(self, tmp_path, monkeypatch):
        helper = self._make_helper(tmp_path, monkeypatch)
        proc = MagicMock()
        proc.communicate.return_value = (b"ok", b"")
        proc.returncode = 0
        with (
            patch.object(helper, "check_connect"),
            patch("aklog.device.hdc.cmd_runner.popen", return_value=proc),
        ):
            assert helper.run_cmd("shell echo hi") == "ok"
            assert helper.run_file_cmd("file", "recv", "/remote", "/local") == "ok"

    def test_run_cmd_raises_on_failure(self, tmp_path, monkeypatch):
        helper = self._make_helper(tmp_path, monkeypatch)
        with (
            patch.object(helper, "check_connect"),
            patch.object(helper, "run_cmd_result_code", return_value=(1, b"", b"err")),
        ):
            with pytest.raises(subprocess.CalledProcessError):
                helper.run_cmd("shell false")

    def test_cmd_run_iter_yields_lines(self, tmp_path, monkeypatch):
        helper = self._make_helper(tmp_path, monkeypatch)
        proc = MagicMock()
        proc.stdout.readline.side_effect = ["line\n", ""]
        proc.wait.return_value = 0
        with (
            patch.object(helper, "check_connect"),
            patch.object(helper, "popen", return_value=proc),
        ):
            assert list(helper.cmd_run_iter("shell ls")) == ["line\n"]
