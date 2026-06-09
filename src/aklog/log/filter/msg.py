from typing import List, Optional

from aklog.log.filter.match import MatchPolicy, StringMatcher
from aklog.log.format import JsonValueFormat


class MsgProcessor:
    def __init__(
        self,
        include: Optional[List[str]] = None,
        exact: bool = False,
        exclude_fuzzy: Optional[List[str]] = None,
        exclude_exact: Optional[List[str]] = None,
        json_format: Optional[JsonValueFormat] = None,
    ):
        self.include = include
        self.exact = exact
        self.exclude_fuzzy = exclude_fuzzy
        self.exclude_exact = exclude_exact
        self.json_format = json_format

    def accept_msg(self, msg: str) -> bool:
        if StringMatcher.any_exclude(self.exclude_fuzzy, msg, MatchPolicy.FUZZY):
            return False
        if self.exclude_exact and msg in self.exclude_exact:
            return False
        if self.json_format:
            return True
        if self.include:
            if self.exact:
                return msg in self.include
            return StringMatcher.any_include(self.include, msg, MatchPolicy.FUZZY)
        return True

    def process(self, msg: str) -> Optional[str]:
        if not self.accept_msg(msg):
            return None
        if self.json_format:
            return self.json_format.format_content(msg)
        return msg
