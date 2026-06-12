from __future__ import annotations

from unittest.mock import patch

from aklog.app.info import AppInfoHelper
from aklog.log.filter import FilterChain, LevelFilter, MsgProcessor, PackageFilter, PackageMode, TagFilter
from aklog.log.format import JsonValueFormat
from aklog.log.info import LogInfo, LogLevelHelper
from aklog.log.printer import LOG_FIELD_SEP, LogPrintCtr


class FakePlatform:
    def get_foreground_package(self):
        return "com.demo.app"

    def iter_processes(self):
        return [("100", "com.demo.app")]


def _setup_app_info():
    helper = AppInfoHelper(FakePlatform())
    helper._main_process = {"100": "com.demo.app"}
    helper._cur_app_package = "com.demo.app"
    AppInfoHelper._instance = helper


def _log(
    priority: str = "I",
    tag: str = "MyTag",
    msg: str = "hello",
) -> LogInfo:
    log = LogInfo("01-01", "00:00:00.000", "100", "100", priority, tag)
    if msg:
        log.append_msg_content(msg)
    return log


def _printer(
    package: PackageFilter | None = None,
    level: LevelFilter | None = None,
    tag: TagFilter | None = None,
    msg_processor: MsgProcessor | None = None,
) -> LogPrintCtr:
    return LogPrintCtr(
        filters=FilterChain(
            [
                package or PackageFilter(PackageMode.ALL),
                level or LevelFilter(),
                tag or TagFilter(),
            ]
        ),
        msg_processor=msg_processor or MsgProcessor(),
    )


class TestLogPrintCtr:
    def setup_method(self):
        AppInfoHelper._instance = None
        _setup_app_info()

    def teardown_method(self):
        AppInfoHelper._instance = None

    def test_prints_matching_log(self):
        with patch("aklog.log.printer.print_styled") as mock_print:
            _printer().print(_log())
        mock_print.assert_called_once()

    def test_skips_when_package_filtered(self):
        with patch("aklog.log.printer.print_styled") as mock_print:
            _printer(package=PackageFilter(PackageMode.TARGET, ["other"])).print(_log())
        mock_print.assert_not_called()

    def test_skips_when_level_filtered(self):
        with patch("aklog.log.printer.print_styled") as mock_print:
            _printer(level=LevelFilter(threshold=LogLevelHelper.ERROR)).print(_log(priority="I"))
        mock_print.assert_not_called()

    def test_skips_when_tag_filtered(self):
        with patch("aklog.log.printer.print_styled") as mock_print:
            _printer(tag=TagFilter(include=["OtherTag"], exact=True)).print(_log(tag="MyTag"))
        mock_print.assert_not_called()

    def test_skips_when_tag_excluded_fuzzy(self):
        with patch("aklog.log.printer.print_styled") as mock_print:
            _printer(tag=TagFilter(exclude_fuzzy=["Noise"])).print(_log(tag="NoiseTag"))
        mock_print.assert_not_called()

    def test_skips_when_tag_excluded_exact(self):
        with patch("aklog.log.printer.print_styled") as mock_print:
            _printer(tag=TagFilter(exclude_exact=["NoiseTag"])).print(_log(tag="NoiseTagExtra"))
        mock_print.assert_called_once()
        with patch("aklog.log.printer.print_styled") as mock_print:
            _printer(tag=TagFilter(exclude_exact=["NoiseTag"])).print(_log(tag="NoiseTag"))
        mock_print.assert_not_called()

    def test_skips_when_msg_keyword_not_matched(self):
        with patch("aklog.log.printer.print_styled") as mock_print:
            _printer(msg_processor=MsgProcessor(include=["error"])).print(_log(msg="all good"))
        mock_print.assert_not_called()

    def test_skips_when_msg_excluded_fuzzy(self):
        with patch("aklog.log.printer.print_styled") as mock_print:
            _printer(msg_processor=MsgProcessor(exclude_fuzzy=["secret"])).print(_log(msg="contains secret"))
        mock_print.assert_not_called()

    def test_skips_when_msg_excluded_exact(self):
        with patch("aklog.log.printer.print_styled") as mock_print:
            _printer(msg_processor=MsgProcessor(exclude_exact=["secret"])).print(_log(msg="contains secret"))
        mock_print.assert_called_once()
        with patch("aklog.log.printer.print_styled") as mock_print:
            _printer(msg_processor=MsgProcessor(exclude_exact=["secret"])).print(_log(msg="secret"))
        mock_print.assert_not_called()

    def test_prints_with_msg_exact_match(self):
        with patch("aklog.log.printer.print_styled") as mock_print:
            _printer(msg_processor=MsgProcessor(include=["hello"], exact=True)).print(_log(msg="hello"))
        mock_print.assert_called_once()
        with patch("aklog.log.printer.print_styled") as mock_print:
            _printer(msg_processor=MsgProcessor(include=["hello"], exact=True)).print(_log(msg="say hello"))
        mock_print.assert_not_called()

    def test_prints_with_msg_keyword_match(self):
        with patch("aklog.log.printer.print_styled") as mock_print:
            _printer(msg_processor=MsgProcessor(include=["error"])).print(_log(msg="got error here"))
        mock_print.assert_called_once()

    def test_prints_with_json_msg_format(self):
        with patch("aklog.log.printer.print_styled") as mock_print:
            _printer(msg_processor=MsgProcessor(json_format=JsonValueFormat(_keys=["userId"]))).print(
                _log(msg='{"userId":"12345"}')
            )
        mock_print.assert_called_once()
        assert "userId" in str(mock_print.call_args[0][0])

    def test_filter_chain_and_msg_processor_both_apply(self):
        with patch("aklog.log.printer.print_styled") as mock_print:
            printer = _printer(
                tag=TagFilter(include=["MyTag"], exact=True),
                msg_processor=MsgProcessor(include=["error"]),
            )
            printer.print(_log(tag="MyTag", msg="all good"))
            printer.print(_log(tag="Other", msg="got error"))
            printer.print(_log(tag="MyTag", msg="got error"))
        assert mock_print.call_count == 1

    def test_print_none_is_noop(self):
        with patch("aklog.log.printer.print_styled") as mock_print:
            _printer().print(None)
        mock_print.assert_not_called()

    def test_output_uses_pipe_delimiter(self):
        with patch("aklog.log.printer.print_styled") as mock_print:
            _printer().print(_log(msg="POST:https://example.com/path"))
        line = str(mock_print.call_args[0][0])
        assert LOG_FIELD_SEP in line
        assert "POST:https://example.com/path" in line
        assert "#" not in line.split("POST:https://example.com/path")[0]
