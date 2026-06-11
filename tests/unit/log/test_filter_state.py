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

    def test_summary_with_package_and_level(self):
        state = FilterState(
            profile_name="default",
            package_mode="target",
            package=["com.foo"],
            tag=["Net"],
            msg=["err"],
            level="E",
        )
        summary = state.summary()
        assert "TARGET:com.foo" in summary
        assert "lvl:E" in summary

    def test_from_filter_profile(self):
        profile = FilterProfile(package_mode="target", package=["com.foo"], tag=["Net"])
        state = FilterState.from_filter_profile(profile, "default", "android")
        assert state.package == ["com.foo"]
        assert state.tag == ["Net"]

    def test_to_filter_profile_and_args(self):
        state = FilterState(package_mode="all", tag=["A"], level="W")
        profile = state.to_filter_profile()
        assert profile.package_mode == "all"
        args = state.to_args_dict()
        assert args["level"] == ["W"]

    def test_copy(self):
        state = FilterState(tag=["x"])
        copy = state.copy()
        copy.tag.append("y")
        assert state.tag == ["x"]

    def test_from_args_dict_package_modes(self):
        top = FilterState.from_args_dict({"package_current_top": True})
        assert top.package_mode == "top"
        all_pkgs = FilterState.from_args_dict({"package_all": True})
        assert all_pkgs.package_mode == "all"
        exclude = FilterState.from_args_dict({"package_not": ["com.bad"]})
        assert exclude.package_mode == "exclude"
        target = FilterState.from_args_dict({"package": ["com.good"]})
        assert target.package_mode == "target"

    def test_from_args_dict_tags_and_msgs(self):
        state = FilterState.from_args_dict(
            {
                "tag_exact": ["Exact"],
                "tag_not": ["Skip"],
                "tag_not_exact": ["Skip2"],
                "msg": ["hello"],
                "msg_exact": ["world"],
                "msg_not": ["noise"],
                "msg_not_exact": ["noise2"],
                "level": ["E"],
            }
        )
        assert state.tag == ["Exact"] and state.tag_exact is True
        assert state.tag_exclude == ["Skip"]
        assert state.msg == ["world"] and state.msg_exact is True
        assert state.level == "E"

    def test_from_args_dict_level_scalar(self):
        state = FilterState.from_args_dict({"level": "I"})
        assert state.level == "I"

    def test_apply_to_platform_override(self):
        state = FilterState(package_mode="target", package=["com.foo"], tag=["T"], tag_exact=True)
        override = state.apply_to_platform_override("android")
        assert override.package == ["com.foo"]
        assert override.tag_exact is True
