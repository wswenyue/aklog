from __future__ import annotations

from aklog.core.filter_config import FilterProfile
from aklog.log.filter_state import FilterState


class TestFilterState:
    def test_summary_includes_profile(self):
        state = FilterState(profile_name="work", package_mode="all")
        assert "profile:work" in state.summary()

    def test_dirty_marker(self):
        state = FilterState(profile_name="default", dirty=True)
        assert "default*" in state.summary()

    def test_from_filter_profile(self):
        profile = FilterProfile(package_mode="target", package=["com.foo"], tag=["Net"])
        state = FilterState.from_filter_profile(profile, "default", "android")
        assert state.package == ["com.foo"]
        assert state.tag == ["Net"]
