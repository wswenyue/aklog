from __future__ import annotations

import pytest

from aklog.app.info import AppInfoHelper
from aklog.log.filters import (
    LogLevelFilterFormat,
    LogMsgFilterFormat,
    LogPackageFilterFormat,
    LogTagFilterFormat,
    PackageFilterType,
)
from aklog.log.format import JsonValueFormat


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


class TestLogPackageFilter:
    def test_all_accepts_everything(self):
        flt = LogPackageFilterFormat(PackageFilterType.All)
        assert flt.filter("anything") is True

    def test_target_partial_match(self):
        flt = LogPackageFilterFormat(PackageFilterType.TARGET, ["example"])
        assert flt.filter("com.example.app") is True
        assert flt.filter("com.other.app") is False

    def test_exclude(self):
        flt = LogPackageFilterFormat(PackageFilterType.EXCLUDE, ["system"])
        assert flt.filter("com.example.app") is True
        assert flt.filter("com.android.system") is False

    def test_top_uses_foreground_package(self):
        AppInfoHelper._instance = AppInfoHelper(FakePlatform())
        AppInfoHelper._instance._cur_app_package = "com.example.app"
        flt = LogPackageFilterFormat(PackageFilterType.Top)
        assert flt.filter("com.example.app:main") is True
        assert flt.filter("com.other.app") is False


class TestLogTagFilter:
    def test_exact_tag(self):
        flt = LogTagFilterFormat(target=["MyTag"], is_exact=True)
        assert flt.filter("MyTag") is True
        assert flt.filter("MyTagExtra") is False

    def test_fuzzy_tag_not(self):
        flt = LogTagFilterFormat(tag_not=["Noise"], is_tag_not_fuzzy=True)
        assert flt.filter("CleanTag") is True
        assert flt.filter("NoiseTag") is False


class TestLogMsgFilter:
    def test_keyword_match(self):
        flt = LogMsgFilterFormat(target=["error"])
        assert flt.format_content("got error here") == "got error here"
        assert flt.format_content("all good") is None

    def test_msg_not(self):
        flt = LogMsgFilterFormat(msg_not=["secret"])
        assert flt.format_content("public info") == "public info"
        assert flt.format_content("contains secret") is None

    def test_json_format(self):
        flt = LogMsgFilterFormat(json_format=JsonValueFormat(_keys=["userId"]))
        out = flt.format_content('{"userId":"12345"}')
        assert out is not None
        assert "userId" in out


class TestLogLevelFilter:
    def test_level_threshold(self):
        flt = LogLevelFilterFormat(target=5)
        assert flt.filter("E") is True
        assert flt.filter("W") is True
        assert flt.filter("I") is False
