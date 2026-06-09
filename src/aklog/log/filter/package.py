from enum import Enum
from typing import List, Optional

from aklog.app.info import AppInfoHelper
from aklog.core import comm_tools
from aklog.log.filter.match import MatchPolicy, StringMatcher
from aklog.log.info import LogInfo


class PackageMode(Enum):
    TOP = 0
    ALL = 1
    TARGET = 2
    EXCLUDE = 3


class PackageFilter:
    def __init__(self, mode: PackageMode, targets: Optional[List[str]] = None):
        self.mode = mode
        self.targets = targets

    def accept(self, log: LogInfo) -> bool:
        return self.accept_package(log.get_process_name())

    def accept_package(self, package: str) -> bool:
        if self.mode == PackageMode.TOP:
            return AppInfoHelper.cur_app_package() in package
        if self.mode == PackageMode.ALL:
            return True
        if self.mode == PackageMode.TARGET:
            if comm_tools.is_empty(self.targets):
                return False
            return StringMatcher.any_include(self.targets, package, MatchPolicy.SUBSTRING)
        if self.mode == PackageMode.EXCLUDE:
            if comm_tools.is_empty(self.targets):
                return True
            return not StringMatcher.any_exclude(self.targets, package, MatchPolicy.FUZZY)
        return True
