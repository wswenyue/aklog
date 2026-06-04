from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from aklog.device.manager import list_all_devices, resolve_device
from aklog.device.platform import PLATFORM_ANDROID, PLATFORM_HARMONY, DeviceInfo


class TestListAllDevices:
    def test_merges_android_and_harmony(self):
        android = [DeviceInfo(PLATFORM_ANDROID, "adb-1", "adb-1")]
        harmony = [DeviceInfo(PLATFORM_HARMONY, "hdc-1", "hdc-1")]
        with (
            patch("aklog.device.manager.AndroidPlatform.list_devices", return_value=android),
            patch("aklog.device.manager.HarmonyPlatform.list_devices", return_value=harmony),
        ):
            devices = list_all_devices()
        assert len(devices) == 2

    def test_swallows_list_errors(self):
        with (
            patch("aklog.device.manager.AndroidPlatform.list_devices", side_effect=OSError("boom")),
            patch("aklog.device.manager.HarmonyPlatform.list_devices", return_value=[]),
        ):
            assert list_all_devices() == []


class TestResolveDevice:
    def test_raises_when_no_devices(self):
        with patch("aklog.device.manager.list_all_devices", return_value=[]):
            with pytest.raises(ValueError, match="No device connected"):
                resolve_device()

    def test_resolves_by_device_id(self):
        info = DeviceInfo(PLATFORM_ANDROID, "dev-a", "dev-a")
        platform = MagicMock()
        with (
            patch("aklog.device.manager.list_all_devices", return_value=[info]),
            patch("aklog.device.manager._create_platform", return_value=platform),
        ):
            result = resolve_device("dev-a")
        assert result is platform
        platform.check_connect.assert_called_once()

    def test_unknown_device_id_raises(self):
        info = DeviceInfo(PLATFORM_ANDROID, "dev-a", "dev-a")
        with patch("aklog.device.manager.list_all_devices", return_value=[info]):
            with pytest.raises(ValueError, match='Device "missing" not found'):
                resolve_device("missing")

    def test_single_device_auto_select(self):
        info = DeviceInfo(PLATFORM_HARMONY, "only-one", "only-one")
        platform = MagicMock()
        with (
            patch("aklog.device.manager.list_all_devices", return_value=[info]),
            patch("aklog.device.manager._create_platform", return_value=platform),
        ):
            result = resolve_device()
        assert result is platform

    def test_prompts_when_multiple_devices(self, monkeypatch):
        devices = [
            DeviceInfo(PLATFORM_ANDROID, "a", "a"),
            DeviceInfo(PLATFORM_HARMONY, "b", "b"),
        ]
        platform = MagicMock()
        monkeypatch.setattr("aklog.device.manager.comm_tools.prompt_choice", lambda _labels, _title: 1)
        with (
            patch("aklog.device.manager.list_all_devices", return_value=devices),
            patch("aklog.device.manager._create_platform", return_value=platform),
        ):
            result = resolve_device()
        assert result is platform
