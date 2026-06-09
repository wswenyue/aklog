from typing import Protocol

from aklog.log.info import LogInfo


class LogFilter(Protocol):
    def accept(self, log: LogInfo) -> bool: ...
