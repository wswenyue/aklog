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
    WUBA_REQ_LINE = (
        "06-12 10:09:31.245 16932 16932 D A00001/com.wuba.bangjob.hap/[WubaApp][NetLogPrinterReq]: "
        "[1245]Request>>> [cmd:default] POST:https://zppost.58.com/zcm/ajax/searchTrustedAddress "
        '[args]{"uniqueness_request_cmd":"default","hrEntId":"0"}'
    )

    def test_parses_single_line_with_message(self):
        printer = MagicMock()
        parser = HilogMsgParser(printer)
        parser.parser(HILOG_LINE)
        printer.print.assert_not_called()
        assert parser.log is not None
        assert parser.log.tag == "testTag"
        assert parser.log.get_msg_content() == "hello world"
        parser.parser(HILOG_LINE.replace("hello world", "next entry"))
        printer.print.assert_called_once()
        printed = printer.print.call_args[0][0]
        assert printed.get_msg_content() == "hello world"

    def test_appends_continuation_lines(self):
        printer = MagicMock()
        parser = HilogMsgParser(printer)
        parser.parser("04-19 17:02:14.735  5394  5394 I A03200/testTag:")
        assert parser.log is not None
        parser.parser("continuation")
        assert "continuation" in parser.log.get_msg_content()
        printer.print.assert_not_called()

    def test_appends_wrap_continuation_after_head_with_content(self):
        printer = MagicMock()
        parser = HilogMsgParser(printer)
        parser.parser(
            "06-12 10:09:31.385 16932 16932 D A00001/com.wuba.bangjob.hap/[WubaApp][NetLogPrinterResp]: "
            '{"resultcode":0,"result":'
        )
        parser.parser('"trustedAddressList":[{"address":"北京"}],"totalCount":199}')
        assert parser.log is not None
        content = parser.log.get_msg_content()
        assert '"resultcode":0' in content
        assert '"totalCount":199' in content
        printer.print.assert_not_called()

    def test_parses_wuba_net_log_with_url_colons(self):
        printer = MagicMock()
        parser = HilogMsgParser(printer)
        parser.parser(self.WUBA_REQ_LINE)
        assert parser.log is not None
        assert parser.log.tag == "[WubaApp][NetLogPrinterReq]"
        content = parser.log.get_msg_content()
        assert "POST:https://zppost.58.com/zcm/ajax/searchTrustedAddress" in content
        assert '[cmd:default]' in content
        assert '"hrEntId":"0"' in content

    def test_flushes_previous_log_on_new_head(self):
        printer = MagicMock()
        parser = HilogMsgParser(printer)
        parser.parser(HILOG_LINE)
        parser.parser(HILOG_LINE.replace("testTag", "OtherTag"))
        printer.print.assert_called_once()

    def test_parses_domain_bundle_tag_format(self):
        printer = MagicMock()
        parser = HilogMsgParser(printer)
        line = "06-09 15:49:56.491  56558  56558 I A03200/com.ganji.job/[wmda]: [session] get uuid"
        parser.parser(line)
        parser.parser(line.replace("[session] get uuid", "next"))
        printed = printer.print.call_args[0][0]
        assert printed.tag == "[wmda]"
        assert printed.get_msg_content() == "[session] get uuid"
