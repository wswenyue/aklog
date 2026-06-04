from __future__ import annotations

from unittest.mock import patch

from aklog.app.info import AppInfoHelper
from aklog.log.filters import (
    LogLevelFilterFormat,
    LogMsgFilterFormat,
    LogPackageFilterFormat,
    LogTagFilterFormat,
    PackageFilterType,
)
from aklog.log.info import LogInfo, LogLevelHelper
from aklog.log.printer import LogPrintCtr


class FakePlatform:
    def get_foreground_package(self):
        return "com.demo.app"

    def iter_processes(self):
        return [("100", "com.demo.app")]


class TestLogPrintCtr:
    def setup_method(self):
        AppInfoHelper._instance = None

    def teardown_method(self):
        AppInfoHelper._instance = None

    def _build_printer(self):
        printer = LogPrintCtr()
        helper = AppInfoHelper(FakePlatform())
        helper._main_process = {"100": "com.demo.app"}
        helper._cur_app_package = "com.demo.app"
        AppInfoHelper._instance = helper
        printer.package = LogPackageFilterFormat(PackageFilterType.All)
        printer.tag = LogTagFilterFormat()
        printer.msg = LogMsgFilterFormat()
        printer.level = LogLevelFilterFormat()
        return printer

    def test_prints_matching_log(self):
        printer = self._build_printer()
        log = LogInfo("01-01", "00:00:00.000", "100", "100", "I", "MyTag")
        log.append_msg_content("hello")
        with patch("builtins.print") as mock_print:
            printer.print(log)
        mock_print.assert_called_once()

    def test_skips_when_package_filtered(self):
        printer = self._build_printer()
        printer.package = LogPackageFilterFormat(PackageFilterType.TARGET, ["other"])
        log = LogInfo("01-01", "00:00:00.000", "100", "100", "I", "MyTag")
        log.append_msg_content("hello")
        with patch("builtins.print") as mock_print:
            printer.print(log)
        mock_print.assert_not_called()

    def test_skips_when_level_filtered(self):
        printer = self._build_printer()
        printer.level = LogLevelFilterFormat(target=LogLevelHelper.ERROR)
        log = LogInfo("01-01", "00:00:00.000", "100", "100", "I", "MyTag")
        log.append_msg_content("hello")
        with patch("builtins.print") as mock_print:
            printer.print(log)
        mock_print.assert_not_called()

    def test_print_none_is_noop(self):
        printer = self._build_printer()
        with patch("builtins.print") as mock_print:
            printer.print(None)
        mock_print.assert_not_called()
