from __future__ import annotations

import pytest

from aklog.app.info import AppInfoHelper
from aklog.log.filter import (
    AcceptAllFilter,
    FilterChain,
    LevelFilter,
    MatchPolicy,
    MsgProcessor,
    PackageFilter,
    PackageMode,
    StringMatcher,
    TagFilter,
)
from aklog.log.format import JsonValueFormat
from aklog.log.info import LogInfo, LogLevelHelper


@pytest.fixture(autouse=True)
def reset_app_info():
    AppInfoHelper._instance = None
    yield
    AppInfoHelper._instance = None


class FakePlatform:
    def get_foreground_package(self):
        return "com.example.app"

    def iter_processes(self):
        return []


def _log(
    priority: str = "I",
    tag: str = "MyTag",
    pid: str = "100",
    msg: str = "hello",
) -> LogInfo:
    log = LogInfo("01-01", "00:00:00.000", pid, pid, priority, tag)
    if msg:
        log.append_msg_content(msg)
    return log


class TestStringMatcher:
    def test_exact_match(self):
        assert StringMatcher.matches("Foo", "Foo", MatchPolicy.EXACT) is True
        assert StringMatcher.matches("Foo", "foo", MatchPolicy.EXACT) is False
        assert StringMatcher.matches("Foo", "FooBar", MatchPolicy.EXACT) is False

    def test_substring_match_is_case_sensitive(self):
        assert StringMatcher.matches("err", "got error here", MatchPolicy.SUBSTRING) is True
        assert StringMatcher.matches("ERR", "got error here", MatchPolicy.SUBSTRING) is False

    def test_fuzzy_match_ignores_case(self):
        assert StringMatcher.matches("system", "com.Android.SystemUI", MatchPolicy.FUZZY) is True
        assert StringMatcher.matches("SYSTEM", "com.android.system", MatchPolicy.FUZZY) is True

    def test_any_include_empty_needles_accepts(self):
        assert StringMatcher.any_include(None, "anything", MatchPolicy.SUBSTRING) is True
        assert StringMatcher.any_include([], "anything", MatchPolicy.SUBSTRING) is True

    def test_any_exclude_empty_needles_rejects_nothing(self):
        assert StringMatcher.any_exclude(None, "anything", MatchPolicy.SUBSTRING) is False
        assert StringMatcher.any_exclude([], "anything", MatchPolicy.SUBSTRING) is False


class TestFilterChain:
    def test_all_filters_must_pass(self):
        chain = FilterChain(
            [
                PackageFilter(PackageMode.ALL),
                LevelFilter(threshold=LogLevelHelper.WARN),
                TagFilter(include=["MyTag"]),
            ]
        )
        assert chain.accept(_log(priority="E", tag="MyTag")) is True
        assert chain.accept(_log(priority="I", tag="MyTag")) is False
        assert chain.accept(_log(priority="E", tag="Other")) is False

    def test_short_circuits_on_first_rejection(self):
        calls = []

        class SpyFilter:
            def accept(self, log: LogInfo) -> bool:
                calls.append("spy")
                return False

        chain = FilterChain([SpyFilter(), PackageFilter(PackageMode.ALL)])
        assert chain.accept(_log()) is False
        assert calls == ["spy"]

    def test_empty_factory_accepts_all(self):
        assert FilterChain.empty().accept(_log()) is True

    def test_exposes_configured_filters(self):
        package = PackageFilter(PackageMode.ALL)
        level = LevelFilter()
        chain = FilterChain([package, level])
        assert chain.filters == (package, level)


class TestPackageFilter:
    def test_all_accepts_everything(self):
        flt = PackageFilter(PackageMode.ALL)
        assert flt.accept_package("anything") is True

    def test_target_partial_match(self):
        flt = PackageFilter(PackageMode.TARGET, ["example"])
        assert flt.accept_package("com.example.app") is True
        assert flt.accept_package("com.other.app") is False

    def test_target_empty_rejects(self):
        flt = PackageFilter(PackageMode.TARGET, [])
        assert flt.accept_package("com.example.app") is False

    def test_exclude(self):
        flt = PackageFilter(PackageMode.EXCLUDE, ["system"])
        assert flt.accept_package("com.example.app") is True
        assert flt.accept_package("com.android.system") is False
        assert flt.accept_package("com.Android.SystemUI") is False

    def test_exclude_empty_accepts_all(self):
        flt = PackageFilter(PackageMode.EXCLUDE, [])
        assert flt.accept_package("com.android.system") is True

    def test_top_uses_foreground_package(self):
        AppInfoHelper._instance = AppInfoHelper(FakePlatform())
        AppInfoHelper._instance._cur_app_package = "com.example.app"
        flt = PackageFilter(PackageMode.TOP)
        assert flt.accept_package("com.example.app:main") is True
        assert flt.accept_package("com.other.app") is False

    def test_accept_uses_process_name(self):
        AppInfoHelper._instance = AppInfoHelper(FakePlatform())
        AppInfoHelper._instance._main_process = {"100": "com.example.app"}
        flt = PackageFilter(PackageMode.TARGET, ["example"])
        assert flt.accept(_log(pid="100")) is True
        assert flt.accept(_log(pid="200")) is False


class TestTagFilter:
    def test_no_rules_accepts_all(self):
        flt = TagFilter()
        assert flt.accept_tag("anything") is True

    def test_exact_tag(self):
        flt = TagFilter(include=["MyTag"], exact=True)
        assert flt.accept_tag("MyTag") is True
        assert flt.accept_tag("MyTagExtra") is False

    def test_fuzzy_tag_ignore_case(self):
        flt = TagFilter(include=["router"])
        assert flt.accept_tag("Router") is True
        assert flt.accept_tag("ROUTER") is True
        assert flt.accept_tag("MyRouter") is True
        assert flt.accept_tag("other") is False

    def test_tag_not_substring_match(self):
        flt = TagFilter(exclude_fuzzy=["Noise"])
        assert flt.accept_tag("CleanTag") is True
        assert flt.accept_tag("NoiseTag") is False
        assert flt.accept_tag("noisetag") is False

    def test_tag_not_excludes_harmony_bundle_tag(self):
        flt = TagFilter(exclude_fuzzy=["wlog"])
        assert flt.accept_tag("com.wuba.bangjob.hap/wlog-c") is False
        assert flt.accept_tag("other-tag") is True

    def test_exclude_runs_before_include(self):
        flt = TagFilter(include=["router"], exclude_fuzzy=["Noise"])
        assert flt.accept_tag("MyRouter") is True
        assert flt.accept_tag("NoiseRouter") is False

    def test_exclude_exact(self):
        flt = TagFilter(exclude_exact=["MyTag"])
        assert flt.accept_tag("MyTag") is False
        assert flt.accept_tag("MyTagExtra") is True
        assert flt.accept_tag("Other") is True

    def test_exclude_fuzzy_and_exact_both_apply(self):
        flt = TagFilter(exclude_fuzzy=["noise"], exclude_exact=["ExactTag"])
        assert flt.accept_tag("NoiseTag") is False
        assert flt.accept_tag("ExactTag") is False
        assert flt.accept_tag("CleanTag") is True

    def test_accept_uses_log_tag(self):
        flt = TagFilter(include=["MyTag"], exact=True)
        assert flt.accept(_log(tag="MyTag")) is True
        assert flt.accept(_log(tag="Other")) is False


class TestMsgProcessor:
    def test_keyword_match(self):
        processor = MsgProcessor(include=["error"])
        assert processor.process("got error here") == "got error here"
        assert processor.process("all good") is None

    def test_keyword_match_ignores_case(self):
        processor = MsgProcessor(include=["error"])
        assert processor.process("got ERROR here") == "got ERROR here"

    def test_any_keyword_matches(self):
        processor = MsgProcessor(include=["timeout", "failed"])
        assert processor.process("request failed") == "request failed"
        assert processor.process("connection timeout") == "connection timeout"
        assert processor.process("ok") is None

    def test_exact_match(self):
        processor = MsgProcessor(include=["error"], exact=True)
        assert processor.process("error") == "error"
        assert processor.process("got error here") is None

    def test_msg_not_fuzzy(self):
        processor = MsgProcessor(exclude_fuzzy=["secret"])
        assert processor.process("public info") == "public info"
        assert processor.process("contains secret") is None

    def test_msg_not_fuzzy_ignores_case(self):
        processor = MsgProcessor(exclude_fuzzy=["secret"])
        assert processor.process("contains SECRET") is None

    def test_msg_not_exact(self):
        processor = MsgProcessor(exclude_exact=["error"])
        assert processor.process("error") is None
        assert processor.process("got error here") == "got error here"

    def test_exclude_fuzzy_and_exact_both_apply(self):
        processor = MsgProcessor(exclude_fuzzy=["noise"], exclude_exact=["ExactMsg"])
        assert processor.process("Noise here") is None
        assert processor.process("ExactMsg") is None
        assert processor.process("clean") == "clean"

    def test_json_format(self):
        processor = MsgProcessor(json_format=JsonValueFormat(_keys=["userId"]))
        out = processor.process('{"userId":"12345"}')
        assert out is not None
        assert "userId" in out

    def test_json_format_skips_keyword_include(self):
        processor = MsgProcessor(
            include=["missing"],
            json_format=JsonValueFormat(_keys=["userId"]),
        )
        out = processor.process('{"userId":"12345"}')
        assert out is not None
        assert "userId" in out

    def test_json_format_without_key_returns_none(self):
        processor = MsgProcessor(json_format=JsonValueFormat(_keys=["userId"]))
        assert processor.process('{"name":"alice"}') is None

    def test_json_respects_exclude_before_format(self):
        processor = MsgProcessor(
            exclude_fuzzy=["secret"],
            json_format=JsonValueFormat(_keys=["userId"]),
        )
        assert processor.process('{"userId":"secret-value"}') is None

    def test_empty_message_without_rules(self):
        processor = MsgProcessor()
        assert processor.process("") == ""


class TestLevelFilter:
    def test_level_threshold(self):
        flt = LevelFilter(threshold=5)
        assert flt.accept_level("E") is True
        assert flt.accept_level("W") is True
        assert flt.accept_level("I") is False

    def test_no_threshold_accepts_all(self):
        flt = LevelFilter()
        assert flt.accept_level("V") is True
        assert flt.accept_level("E") is True

    def test_verbose_threshold(self):
        flt = LevelFilter(threshold=LogLevelHelper.VERBOSE)
        assert flt.accept_level("V") is True
        assert flt.accept_level("D") is True

    def test_accept_uses_log_level(self):
        flt = LevelFilter(threshold=LogLevelHelper.ERROR)
        assert flt.accept(_log(priority="E")) is True
        assert flt.accept(_log(priority="I")) is False


class TestAcceptAllFilter:
    def test_accepts_any_log(self):
        assert AcceptAllFilter().accept(_log()) is True
        assert AcceptAllFilter().accept(_log(priority="V", tag="", msg="")) is True
