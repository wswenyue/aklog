from __future__ import annotations

from unittest.mock import patch

from aklog.cli.args import AkLogCli
from aklog.cli.completion import _device_completer, register_completers
from aklog.device.platform import PLATFORM_ANDROID, DeviceInfo


class TestDeviceCompleter:
    def test_returns_all_device_ids(self):
        devices = [
            DeviceInfo(PLATFORM_ANDROID, "emulator-5554", "emulator-5554"),
            DeviceInfo(PLATFORM_ANDROID, "ABC123", "ABC123"),
        ]
        with patch("aklog.cli.completion.list_all_devices", return_value=devices):
            result = _device_completer("", parsed_args=None)
        assert result == ["emulator-5554", "ABC123"]

    def test_filters_by_prefix(self):
        devices = [
            DeviceInfo(PLATFORM_ANDROID, "emulator-5554", "emulator-5554"),
            DeviceInfo(PLATFORM_ANDROID, "ABC123", "ABC123"),
        ]
        with patch("aklog.cli.completion.list_all_devices", return_value=devices):
            result = _device_completer("emu", parsed_args=None)
        assert result == ["emulator-5554"]

    def test_returns_empty_on_error(self):
        with patch("aklog.cli.completion.list_all_devices", side_effect=RuntimeError("adb missing")):
            result = _device_completer("", parsed_args=None)
        assert result == []


class TestRegisterCompleters:
    def test_register_completers_smoke(self):
        parser = AkLogCli().build_parser()
        register_completers(parser)
        device_actions = [a for a in parser._actions if a.dest == "device"]
        assert device_actions
        assert device_actions[0].completer is _device_completer

    def test_parse_still_works_after_completion_hook(self):
        cli = AkLogCli()
        args = cli.parse([])
        assert args["package_current_top"] is True
