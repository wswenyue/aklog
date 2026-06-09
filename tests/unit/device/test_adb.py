from __future__ import annotations

import subprocess
from unittest.mock import MagicMock, patch

import pytest

from aklog.device.adb import AdbCmd, AdbHelper


@pytest.fixture(autouse=True)
def reset_adb_cache():
    AdbCmd._adb = None
    yield
    AdbCmd._adb = None


class TestAdbCmd:
    def test_find_adb_from_lib_dir(self, tmp_path, monkeypatch):
        adb_bin = tmp_path / "adb"
        adb_bin.write_text("#!/bin/sh\n", encoding="utf-8")
        adb_bin.chmod(0o755)
        monkeypatch.delenv("ANDROID_HOME", raising=False)
        monkeypatch.setattr("aklog.device.adb.bundled_tool", lambda name: str(tmp_path / name))
        assert AdbCmd.find_adb() == str(adb_bin)

    def test_find_adb_missing_returns_none(self, monkeypatch):
        monkeypatch.setattr(
            "aklog.device.adb.bundled_tool",
            lambda name: f"/nonexistent/{name}",
        )
        monkeypatch.delenv("ANDROID_HOME", raising=False)
        assert AdbCmd.find_adb() is None

    def test_find_adb_from_android_home(self, tmp_path, monkeypatch):
        sdk = tmp_path / "platform-tools"
        sdk.mkdir(parents=True)
        adb_bin = sdk / "adb"
        adb_bin.write_text("#!/bin/sh\n", encoding="utf-8")
        adb_bin.chmod(0o755)
        monkeypatch.setenv("ANDROID_HOME", str(tmp_path))
        monkeypatch.setattr(
            "aklog.device.adb.bundled_tool",
            lambda name: f"/nonexistent/{name}",
        )
        assert AdbCmd.find_adb() == str(adb_bin)

    def test_find_adb_explicit_path(self, tmp_path):
        adb_bin = tmp_path / "custom-adb"
        adb_bin.write_text("#!/bin/sh\n", encoding="utf-8")
        adb_bin.chmod(0o755)
        assert AdbCmd.find_adb(str(adb_bin)) == str(adb_bin)


class TestAdbHelper:
    def _make_helper(self, tmp_path, monkeypatch, device_id="dev1"):
        adb_bin = tmp_path / "adb"
        adb_bin.write_text("#!/bin/sh\n", encoding="utf-8")
        adb_bin.chmod(0o755)
        monkeypatch.delenv("ANDROID_HOME", raising=False)
        monkeypatch.setattr("aklog.device.adb.bundled_tool", lambda name: str(tmp_path / name))
        return AdbHelper(device_id=device_id)

    def test_list_connected_devices(self, tmp_path, monkeypatch):
        self._make_helper(tmp_path, monkeypatch)
        lines = ["List of devices attached", "dev1\tdevice", "offline\toffline"]
        with patch("aklog.device.adb.cmd_runner.iter_lines", return_value=iter(lines)):
            assert AdbHelper.list_connected_devices() == ["dev1"]

    def test_check_connect_success(self, tmp_path, monkeypatch):
        helper = self._make_helper(tmp_path, monkeypatch)
        with patch.object(helper, "_AdbHelper__check_adb_connect", return_value=True):
            helper.check_connect()

    def test_check_connect_failure_raises(self, tmp_path, monkeypatch):
        helper = self._make_helper(tmp_path, monkeypatch, device_id="missing")
        with (
            patch.object(helper, "_AdbHelper__check_adb_connect", return_value=False),
            patch.object(helper, "_AdbHelper__restart_adb_connect"),
        ):
            with pytest.raises(ValueError, match='device "missing" not connected'):
                helper.check_connect()

    def test_run_cmd_returns_output(self, tmp_path, monkeypatch):
        helper = self._make_helper(tmp_path, monkeypatch)
        with (
            patch.object(helper, "check_connect"),
            patch.object(helper, "run_cmd_result_code", return_value=(0, b"ok", b"")),
        ):
            assert helper.run_cmd("shell echo hi") == "ok"

    def test_unavailable_adb_raises(self, monkeypatch):
        monkeypatch.setattr(
            "aklog.device.adb.bundled_tool",
            lambda name: f"/nonexistent/{name}",
        )
        monkeypatch.delenv("ANDROID_HOME", raising=False)
        helper = AdbHelper()
        with pytest.raises(OSError, match="adb not found"):
            helper._base_argv()

    def test_device_argv_includes_serial(self, tmp_path, monkeypatch):
        helper = self._make_helper(tmp_path, monkeypatch, device_id="serial-x")
        argv = helper._device_argv("shell echo hi")
        assert argv[:4] == [str(tmp_path / "adb"), "-s", "serial-x", "shell"]

    def test_check_adb_connect_any_device(self, tmp_path, monkeypatch):
        helper = self._make_helper(tmp_path, monkeypatch, device_id=None)
        lines = ["List of devices attached", "dev1\tdevice"]
        with patch("aklog.device.adb.cmd_runner.iter_lines", return_value=iter(lines)):
            assert helper._AdbHelper__check_adb_connect() is True

    def test_check_adb_connect_matching_serial(self, tmp_path, monkeypatch):
        helper = self._make_helper(tmp_path, monkeypatch, device_id="dev1")
        lines = ["List of devices attached", "dev1\tdevice", "dev2\tdevice"]
        with patch("aklog.device.adb.cmd_runner.iter_lines", return_value=iter(lines)):
            assert helper._AdbHelper__check_adb_connect() is True

    def test_check_connect_restarts_and_succeeds(self, tmp_path, monkeypatch):
        helper = self._make_helper(tmp_path, monkeypatch)
        with (
            patch.object(helper, "_AdbHelper__check_adb_connect", side_effect=[False, True]),
            patch.object(helper, "_AdbHelper__restart_adb_connect") as restart,
        ):
            helper.check_connect()
        restart.assert_called_once()

    def test_check_connect_no_device_raises(self, tmp_path, monkeypatch):
        helper = self._make_helper(tmp_path, monkeypatch, device_id=None)
        with (
            patch.object(helper, "_AdbHelper__check_adb_connect", return_value=False),
            patch.object(helper, "_AdbHelper__restart_adb_connect"),
        ):
            with pytest.raises(ValueError, match="no device connected"):
                helper.check_connect()

    def test_run_cmd_raises_on_non_zero(self, tmp_path, monkeypatch):
        helper = self._make_helper(tmp_path, monkeypatch)
        with (
            patch.object(helper, "check_connect"),
            patch.object(helper, "run_cmd_result_code", return_value=(1, b"", b"fail")),
        ):
            with pytest.raises(subprocess.CalledProcessError):
                helper.run_cmd("shell false")

    def test_cmd_run_iter_yields_lines(self, tmp_path, monkeypatch):
        helper = self._make_helper(tmp_path, monkeypatch)
        proc = MagicMock()
        proc.stdout.readline.side_effect = [b"line\n", b""]
        proc.wait.return_value = 0
        with (
            patch.object(helper, "check_connect"),
            patch.object(helper, "popen", return_value=proc),
        ):
            assert list(helper.cmd_run_iter("shell ps")) == ["line\n"]

    def test_popen_passes_kwargs(self, tmp_path, monkeypatch):
        helper = self._make_helper(tmp_path, monkeypatch)
        with patch("aklog.device.adb.cmd_runner.popen") as mock_popen:
            helper.popen("shell ls", stdout=MagicMock(), universal_newlines=True)
        mock_popen.assert_called_once()
