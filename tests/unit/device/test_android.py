from __future__ import annotations

from unittest.mock import MagicMock, patch

from aklog.device.android import AndroidPlatform
from aklog.device.platform import PLATFORM_ANDROID


class TestAndroidPlatform:
    def test_properties(self):
        platform = AndroidPlatform("serial-1")
        assert platform.platform == PLATFORM_ANDROID
        assert platform.device_id == "serial-1"

    def test_list_devices_empty_when_no_adb(self, monkeypatch):
        monkeypatch.setattr("aklog.device.android.AdbCmd.find_adb", lambda: None)
        assert AndroidPlatform.list_devices() == []

    def test_list_devices_from_adb(self, monkeypatch):
        monkeypatch.setattr("aklog.device.android.AdbCmd.find_adb", lambda: "/adb")
        with patch("aklog.device.android.AdbHelper.list_connected_devices", return_value=["d1", "d2"]):
            devices = AndroidPlatform.list_devices()
        assert len(devices) == 2
        assert devices[0].device_id == "d1"

    def test_get_foreground_package_from_activity(self):
        platform = AndroidPlatform("d1")
        platform._helper = MagicMock()
        platform._helper.run_cmd.return_value = "x y com.demo.app/.MainActivity z w"
        assert platform.get_foreground_package() == "com.demo.app"

    def test_get_foreground_package_from_focused_window(self):
        platform = AndroidPlatform("d1")
        platform._helper = MagicMock()
        platform._helper.run_cmd.side_effect = Exception("no activity")
        platform._helper.cmd_run_iter.return_value = iter(
            [
                "mFocusedApp=AppWindowToken{token=Token{abc}} u0 p1 p2 com.other.app/.MainActivity extra",
            ]
        )
        assert platform.get_foreground_package() == "com.other.app"

    def test_iter_processes_filters_system(self):
        platform = AndroidPlatform("d1")
        platform._helper = MagicMock()
        platform._helper.cmd_run_iter.return_value = iter(
            [
                "USER PID PPID VSZ RSS WCHAN PC S NAME",
                "u0_a1 100 1 0 0 0 0 S com.demo.app",
                "u0_a1 101 1 0 0 0 [kworker]",
                "root 1 0 0 0 0 0 init",
            ]
        )
        processes = list(platform.iter_processes())
        assert processes == [("100", "com.demo.app")]

    def test_capture_screen_delegates(self):
        platform = AndroidPlatform("d1")
        platform._helper = MagicMock()
        platform.capture_screen("/sdcard/x.png", "/tmp/x.png")
        assert platform._helper.run_cmd.call_count == 3

    def test_dump_crash_logs_writes_file(self, tmp_path, monkeypatch):
        platform = AndroidPlatform("d1")
        platform._helper = MagicMock()
        platform._helper.cmd_run_iter.return_value = iter(
            [
                "2024-01-01 data_app_crash",
            ]
        )
        platform._helper.run_cmd.return_value = "crash body"
        monkeypatch.setattr(
            "aklog.device.android.comm_tools.get_user_desktop_dir",
            lambda name=None: str(tmp_path),
        )
        platform.dump_crash_logs(is_native=False, max_size=1, save_dir=None)
        files = list(tmp_path.glob("*.log"))
        assert len(files) == 1
        assert "crash body" in files[0].read_text(encoding="utf-8")
