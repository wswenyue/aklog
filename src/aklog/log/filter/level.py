from typing import Optional

from aklog.log.info import LogInfo, LogLevelHelper


class LevelFilter:
    def __init__(self, threshold: Optional[int] = None):
        self.threshold = threshold

    def accept(self, log: LogInfo) -> bool:
        return self.accept_level(log.get_level_name())

    def accept_level(self, level: str) -> bool:
        if self.threshold:
            return self.threshold <= LogLevelHelper.level_code(level)
        return True
