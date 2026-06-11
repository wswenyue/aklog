from typing import Iterable, Tuple

from aklog.log.filter.protocol import LogFilter
from aklog.log.info import LogInfo


class AcceptAllFilter:
    def accept(self, log: LogInfo) -> bool:
        return True


class FilterChain:
    def __init__(self, filters: Iterable[LogFilter] = ()):
        self._filters: Tuple[LogFilter, ...] = tuple(filters)

    @property
    def filters(self) -> Tuple[LogFilter, ...]:
        return self._filters

    def accept(self, log: LogInfo) -> bool:
        return all(f.accept(log) for f in self._filters)

    def replace_filters(self, filters: Iterable[LogFilter]) -> None:
        self._filters = tuple(filters)

    @classmethod
    def empty(cls) -> "FilterChain":
        return cls([AcceptAllFilter()])
