from __future__ import annotations

from unittest.mock import MagicMock, patch

from aklog.tools.dump_crash import DumpCrashLog
from aklog.tools.record_video import PhoneRecordVideo, RecordHelper
from aklog.tools.screen_cap import ScreenCapTools


class FakePlatform:
    platform = "android"

    def phone_tmp_dir(self):
        return "/sdcard/"

    def screen_cap_ext(self):
        return ".png"

    def capture_screen(self, phone_path, local_path):
        from pathlib import Path

        Path(local_path).write_bytes(b"fake-png")
        self.last = (phone_path, local_path)


class TestScreenCapTools:
    def test_do_capture(self, tmp_path, monkeypatch):
        monkeypatch.setattr("aklog.tools.screen_cap.comm_tools.is_mac_os", lambda: False)
        platform = FakePlatform()
        tool = ScreenCapTools(platform, str(tmp_path))
        with patch("builtins.print"):
            tool.do_capture()
        assert any(tmp_path.glob("*.png"))


class TestDumpCrashLog:
    def test_do_work_delegates(self):
        platform = MagicMock()
        worker = DumpCrashLog(platform, is_ndk=True, dir="/tmp", max_size=3)
        worker.do_work()
        platform.dump_crash_logs.assert_called_once_with(True, 3, "/tmp")


class TestPhoneRecordVideo:
    def test_android_record_and_pull(self, tmp_path):
        platform = MagicMock()
        platform.platform = "android"
        proc = MagicMock()
        platform.start_screen_record.return_value = proc
        platform.stop_screen_record.return_value = "/sdcard/video.mp4"
        video = PhoneRecordVideo(platform, str(tmp_path))
        with patch("builtins.print"):
            video.do_record()
            video.do_pull()
            video.do_clean()
        platform.pull_file.assert_called_once()
        platform.remove_remote_file.assert_called_once()

    def test_record_helper_starts_recording(self, monkeypatch):
        platform = MagicMock()
        platform.platform = "android"
        proc = MagicMock()
        platform.start_screen_record.return_value = proc
        monkeypatch.setattr("aklog.tools.record_video.signal.signal", lambda *_args: None)
        with patch("builtins.print"):
            RecordHelper.do_work(platform, "/tmp")

    def test_harmony_record_loop_exits(self, tmp_path, monkeypatch):
        platform = MagicMock()
        platform.platform = "harmony"
        video = PhoneRecordVideo(platform, str(tmp_path))
        video.isDoExitWork = True
        with patch("builtins.print"):
            video.do_record()

    def test_harmony_pull_with_resolved_path(self, tmp_path):
        platform = MagicMock()
        platform.platform = "harmony"
        platform.stop_screen_record.return_value = "/data/video.mp4"
        video = PhoneRecordVideo(platform, str(tmp_path))
        with patch("builtins.print"):
            video.do_pull()
        platform.pull_file.assert_called_once()

    def test_harmony_pull_without_resolved_path(self, tmp_path):
        platform = MagicMock()
        platform.platform = "harmony"
        video = PhoneRecordVideo(platform, str(tmp_path))
        platform.stop_screen_record.return_value = video.videoName
        with patch("builtins.print"):
            video.do_pull()
        platform.pull_file.assert_not_called()

    def test_record_helper_exit_handler(self, tmp_path, monkeypatch):
        platform = MagicMock()
        platform.platform = "android"
        platform.stop_screen_record.return_value = "/sdcard/video.mp4"
        RecordHelper.curRecord = PhoneRecordVideo(platform, str(tmp_path))
        with (
            patch("builtins.print"),
            patch("aklog.tools.record_video.time.sleep"),
            patch("aklog.tools.record_video.exit") as mock_exit,
        ):
            RecordHelper._exit(None, None)
        mock_exit.assert_called_once()
        assert RecordHelper.curRecord is None
