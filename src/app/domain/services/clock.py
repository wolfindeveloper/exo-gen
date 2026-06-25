from abc import ABC, abstractmethod
from datetime import datetime, date


class Clock(ABC):
    @abstractmethod
    def now(self) -> datetime:
        pass

    @abstractmethod
    def today(self) -> date:
        pass


class SystemClock(Clock):
    def now(self) -> datetime:
        from datetime import timezone
        return datetime.now(timezone.utc)

    def today(self) -> date:
        return date.today()
