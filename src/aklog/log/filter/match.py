from enum import Enum
from typing import List, Optional

from aklog.core import comm_tools


class MatchPolicy(Enum):
    EXACT = "exact"
    SUBSTRING = "substring"
    FUZZY = "fuzzy"


class StringMatcher:
    @staticmethod
    def matches(needle: str, haystack: str, policy: MatchPolicy) -> bool:
        if policy == MatchPolicy.EXACT:
            return comm_tools.match_str(needle, haystack, is_exact=True, is_ignore_case=False)
        if policy == MatchPolicy.SUBSTRING:
            return comm_tools.match_str(needle, haystack, is_exact=False, is_ignore_case=False)
        return comm_tools.match_str(needle, haystack, is_exact=False, is_ignore_case=True)

    @staticmethod
    def any_include(
        needles: Optional[List[str]],
        haystack: str,
        policy: MatchPolicy,
    ) -> bool:
        if comm_tools.is_empty(needles):
            return True
        for needle in needles:
            if StringMatcher.matches(needle, haystack, policy):
                return True
        return False

    @staticmethod
    def any_exclude(
        needles: Optional[List[str]],
        haystack: str,
        policy: MatchPolicy,
    ) -> bool:
        if comm_tools.is_empty(needles):
            return False
        for needle in needles:
            if StringMatcher.matches(needle, haystack, policy):
                return True
        return False
