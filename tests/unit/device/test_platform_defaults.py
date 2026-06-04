from __future__ import annotations

from unittest.mock import MagicMock

from aklog.device.android import AndroidPlatform
from aklog.device.platform import PLATFORM_HARMONY


class TestDevicePlatformDefaults:
    def test_android_tmp_dir_and_ext(self):
        platform = AndroidPlatform("d1")
        assert platform.phone_tmp_dir() == "/sdcard/"
        assert platform.screen_cap_ext() == ".png"

    def test_harmony_defaults_via_mock(self):
        from aklog.device.harmony import HarmonyPlatform

        platform = HarmonyPlatform("t1")
        assert platform.platform == PLATFORM_HARMONY
        assert platform.phone_tmp_dir() == "/data/local/tmp/"
        assert platform.screen_cap_ext() == ".jpeg"

    def test_install_and_record_helpers(self):
        platform = AndroidPlatform("d1")
        platform._helper = MagicMock()
        proc = MagicMock()
        platform._helper.popen.return_value = proc
        assert platform.start_screen_record("v.mp4") is proc
        platform.install_package("/tmp/a.apk")
        platform._helper.run_cmd.assert_called()
