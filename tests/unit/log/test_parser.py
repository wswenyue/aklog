from __future__ import annotations

from unittest.mock import MagicMock

from aklog.log.parser import HilogMsgParser, LogMsgParser

LOGCAT_HEAD = "[ 08-28 22:39:39.974  1785: 1832 D/HeadsetStateMachine ]"
HILOG_LINE = "04-19 17:02:14.735  5394  5394 I A03200/testTag: hello world"


class TestLogMsgParser:
    def test_parses_head_and_message_lines(self):
        printer = MagicMock()
        parser = LogMsgParser(printer)
        parser.parser(LOGCAT_HEAD)
        assert parser.log is not None
        assert parser.log.tag.strip() == "HeadsetStateMachine"
        parser.parser("second line")
        assert "second line" in parser.log.get_msg_content()

    def test_flushes_previous_log_on_new_head(self):
        printer = MagicMock()
        parser = LogMsgParser(printer)
        parser.parser(LOGCAT_HEAD)
        parser.parser(LOGCAT_HEAD.replace("HeadsetStateMachine", "OtherTag"))
        assert printer.print.call_count == 1


class TestHilogMsgParser:
    def test_parses_single_line_with_message(self):
        printer = MagicMock()
        parser = HilogMsgParser(printer)
        parser.parser(HILOG_LINE)
        printer.print.assert_called_once()
        printed = printer.print.call_args[0][0]
        assert printed.tag == "testTag"
        assert printed.get_msg_content() == "hello world"

    def test_appends_continuation_lines(self):
        printer = MagicMock()
        parser = HilogMsgParser(printer)
        parser.parser("04-19 17:02:14.735  5394  5394 I A03200/testTag:")
        assert parser.log is not None
        parser.parser("continuation")
        assert "continuation" in parser.log.get_msg_content()

    def test_parses_domain_bundle_tag_format(self):
        printer = MagicMock()
        parser = HilogMsgParser(printer)
        parser.parser(
            "06-09 15:49:56.491  56558  56558 I A03200/com.ganji.job/[wmda]: [session] get uuid"
        )
        printed = printer.print.call_args[0][0]
        assert printed.tag == "[wmda]"
        assert printed.get_msg_content() == "[session] get uuid"
