from __future__ import annotations

import pytest

from aklog.app.info import AppInfoHelper
from aklog.log.info import LogInfo, LogLevelHelper


@pytest.fixture(autouse=True)
def reset_app_info():
    AppInfoHelper._instance = None
    yield
    AppInfoHelper._instance = None


class FakePlatform:
    def __init__(self, fg="com.demo.app", processes=None):
        self._fg = fg
        self._processes = processes or []

    def get_foreground_package(self):
        return self._fg

    def iter_processes(self):
        return iter(self._processes)


class TestLogLevelHelper:
    @pytest.mark.parametrize(
        "value,expected",
        [
            ("V", LogLevelHelper.VERBOSE),
            ("d", LogLevelHelper.DEBUG),
            ("I", LogLevelHelper.INFO),
            ("W", LogLevelHelper.WARN),
            ("E", LogLevelHelper.ERROR),
            ("?", LogLevelHelper.UNKNOWN),
        ],
    )
    def test_level_code(self, value, expected):
        assert LogLevelHelper.level_code(value) == expected

    def test_level_name_roundtrip(self):
        assert LogLevelHelper.level_name(LogLevelHelper.ERROR) == "E"


class TestLogInfo:
    def test_show_name_main_and_child(self):
        platform = FakePlatform(processes=[("100", "com.demo.app"), ("101", "com.demo.app:service")])
        AppInfoHelper._instance = AppInfoHelper(platform)
        AppInfoHelper._instance._main_process = {"100": "com.demo.app"}
        AppInfoHelper._instance._children_process = {"101": "com.demo.app:service"}

        main = LogInfo("01-01", "00:00:00.000", "100", "100", "I", "Tag")
        child = LogInfo("01-01", "00:00:00.000", "101", "102", "I", "Tag")
        assert main.get_show_name() == "app@main"
        assert child.get_show_name() == "app@service"
        assert child.get_show_tid().startswith("102")

    def test_append_msg_content_multiline(self):
        info = LogInfo("01-01", "00:00:00.000", "1", "1", "I", "Tag")
        info.append_msg_content("line1")
        info.append_msg_content("line2")
        assert "line1" in info.get_msg_content()
        assert "line2" in info.get_msg_content()
