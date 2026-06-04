from __future__ import annotations

import aklog


class TestPackageInit:
    def test_version_is_string(self):
        assert isinstance(aklog.__version__, str)
        assert aklog.__version__.startswith("v")
