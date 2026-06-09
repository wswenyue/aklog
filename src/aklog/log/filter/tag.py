from typing import List, Optional

from aklog.log.filter.match import MatchPolicy, StringMatcher
from aklog.log.info import LogInfo


class TagFilter:
    def __init__(
        self,
        include: Optional[List[str]] = None,
        exact: bool = False,
        exclude_fuzzy: Optional[List[str]] = None,
        exclude_exact: Optional[List[str]] = None,
    ):
        self.include = include
        self.exact = exact
        self.exclude_fuzzy = exclude_fuzzy
        self.exclude_exact = exclude_exact

    def accept(self, log: LogInfo) -> bool:
        return self.accept_tag(log.tag)

    def accept_tag(self, tag: str) -> bool:
        if StringMatcher.any_exclude(self.exclude_fuzzy, tag, MatchPolicy.FUZZY):
            return False
        if self.exclude_exact and tag in self.exclude_exact:
            return False
        if self.include:
            if self.exact:
                return tag in self.include
            return StringMatcher.any_include(self.include, tag, MatchPolicy.FUZZY)
        return True
