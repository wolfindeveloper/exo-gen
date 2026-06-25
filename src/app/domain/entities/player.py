from dataclasses import dataclass, field
from datetime import date, timedelta
from uuid import UUID

from app.domain.exceptions.player import InsufficientFragmentsError
from app.domain.services.clock import Clock, SystemClock
from .ship import Ship


@dataclass
class Player:
    id: UUID
    telegram_id: int
    username: str | None
    xp: int = 0
    xgen_balance: int  = 0
    fragments_balance: int = 0
    daily_streak: int = 0
    last_login_date: date | None = None
    ships: list[Ship] = field(default_factory=list)

    def process_daily_login(self, clock: Clock = None):
        if clock is None:
            clock = SystemClock()

        today = clock.today()

        if self.last_login_date == today:
            return DailyLoginResult(
            earned_xp=0,
            new_streak=self.daily_streak,
            got_box=False,
            already_claimed=True
        )
        
        elif self.last_login_date is None or self.last_login_date == (today - timedelta(days=1)):
            self.daily_streak += 1

        else:
            self.daily_streak = 1

        self.last_login_date = today
        earned_xp = 10 * self.daily_streak
        self.xp += earned_xp

        got_box = (self.daily_streak % 42 == 0) and (self.daily_streak > 0)

        return DailyLoginResult(
            earned_xp=earned_xp,
            new_streak=self.daily_streak,
            got_box=got_box,
            already_claimed=False
        )

    def spend_fragments(self, amount: int) -> None:
        if self.fragments_balance < amount:
            raise InsufficientFragmentsError(required=amount, available=self.fragments_balance)

        self.fragments_balance -= amount

    def add_xgen(self, amount: int) -> None:
        self.xgen_balance += amount

    def add_fragments(self, amount: int) -> None:
        self.fragments_balance += amount


@dataclass
class DailyLoginResult:
    earned_xp: int
    new_streak: int
    got_box: bool = False
    already_claimed: bool = False
