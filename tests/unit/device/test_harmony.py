from __future__ import annotations

from unittest.mock import MagicMock

from aklog.device.harmony import HarmonyPlatform
from aklog.device.platform import PLATFORM_HARMONY


class TestHarmonyPlatform:
    def test_properties(self):
        platform = HarmonyPlatform("target-1")
        assert platform.platform == PLATFORM_HARMONY
        assert platform.device_id == "target-1"

    def test_list_devices_empty_when_no_hdc(self, monkeypatch):
        monkeypatch.setattr("aklog.device.harmony.HdcCmd.find_hdc", lambda: None)
        assert HarmonyPlatform.list_devices() == []

    def test_hilog_level_flag(self):
        platform = HarmonyPlatform("t1")
        assert platform._hilog_level_flag("E") == "E"
        assert platform._hilog_level_flag("V") == "V"
        assert platform._hilog_level_flag("?") == ""

    def test_get_foreground_package(self):
        platform = HarmonyPlatform("t1")
        platform._helper = MagicMock()
        platform._helper.run_cmd.return_value = "Mission ID #100\nFOREGROUND\nbundle name [com.demo.hap]\n"
        assert platform.get_foreground_package() == "com.demo.hap"

    def test_iter_processes(self):
        platform = HarmonyPlatform("t1")
        platform._helper = MagicMock()
        platform._helper.run_cmd.return_value = "\n".join(
            [
                "UID             PID   PPID C STIME TTY          TIME CMD",
                "20020227      55477    607 0 21:05:44 ?     00:00:25 com.demo.hap",
                "20020227      55478    607 0 21:05:44 ?     00:00:01 com.demo.hap:ui",
                "root             67     63 5 12:01:16 ?     02:31:30 devhost.elf /lib/libdh-linux.so",
            ]
        )
        processes = list(platform.iter_processes())
        assert ("55477", "com.demo.hap") in processes
        assert ("55478", "com.demo.hap:ui") in processes

    def test_looks_like_bundle_name(self):
        assert HarmonyPlatform._looks_like_bundle_name("com.demo.hap") is True
        assert HarmonyPlatform._looks_like_bundle_name("com.demo.hap:ui") is True
        assert HarmonyPlatform._looks_like_bundle_name("crypto.elf") is False
        assert HarmonyPlatform._looks_like_bundle_name("init") is False

    def test_phone_tmp_dir_and_ext(self):
        platform = HarmonyPlatform("t1")
        assert platform.phone_tmp_dir() == "/data/local/tmp/"
        assert platform.screen_cap_ext() == ".jpeg"

    def test_start_log_stream_with_level(self):
        platform = HarmonyPlatform("t1")
        platform._helper = MagicMock()
        platform.start_log_stream(level="W")
        cmd = platform._helper.popen.call_args[0][0]
        assert "hilog -L W" in cmd

    def test_dump_crash_logs(self, tmp_path, monkeypatch):
        platform = HarmonyPlatform("t1")
        platform._helper = MagicMock()
        crash_file = tmp_path / "appcrash-1.log"
        crash_file.write_text("crash content", encoding="utf-8")
        platform._helper.run_cmd.return_value = "appcrash-1.log\n"

        def fake_pull(remote, local):
            with open(local, "w", encoding="utf-8") as fp:
                fp.write("crash content")

        platform.pull_file = MagicMock(side_effect=fake_pull)
        monkeypatch.setattr(
            "aklog.device.harmony.comm_tools.get_user_desktop_dir",
            lambda name=None: str(tmp_path),
        )
        platform.dump_crash_logs(is_native=False, max_size=1, save_dir=str(tmp_path))
        merged = list(tmp_path.glob("app_*.log"))
        assert merged

    def test_capture_screen(self):
        platform = HarmonyPlatform("t1")
        platform._helper = MagicMock()
        platform.capture_screen("/data/local/tmp/x.jpeg", "/tmp/x.jpeg")
        assert platform._helper.run_cmd.call_count == 2
        platform._helper.run_file_cmd.assert_called_once()

    def test_install_package(self):
        platform = HarmonyPlatform("t1")
        platform._helper = MagicMock()
        platform.install_package("/tmp/app.hap")
        platform._helper.run_cmd.assert_called_with("install -r /tmp/app.hap")

    def test_stop_screen_record_resolves_path(self):
        platform = HarmonyPlatform("t1")
        platform._helper = MagicMock()
        platform._record_name = "R0101.mp4"
        platform._helper.run_cmd.return_value = "line1\n/data/Media/video.mp4\n"
        assert platform.stop_screen_record("R0101.mp4") == "/data/Media/video.mp4"
