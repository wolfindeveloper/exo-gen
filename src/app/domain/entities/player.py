from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from uuid import UUID

from app.domain.services.clock import Clock, SystemClock
from app.domain.services.level_progression import LevelProgressionService
from app.domain.value_objects.resources import XgenBalance, FragmentsBalance
from app.domain.events.player_events import DailyLoginCompletedEvent
from app.domain.entities.base import AggregateRoot
from .ship import Ship


@dataclass
class Player(AggregateRoot):
    id: UUID
    telegram_id: int
    username: str | None
    xp: int = 0
    xgen_balance: XgenBalance = XgenBalance(0)
    fragments_balance: FragmentsBalance = FragmentsBalance(0)
    daily_streak: int = 0
    last_login_date: date | None = None
    ships: list[Ship] = field(default_factory=list)
    total_expeditions: int = 0
    total_artifacts_found: int = 0
    deleted_at: datetime | None = None

    def soft_delete(self) -> None:
        self.deleted_at = datetime.now(timezone.utc)

    def increment_expeditions(self) -> None:
        self.total_expeditions += 1

    def increment_artifacts_found(self, count: int = 1) -> None:
        self.total_artifacts_found += count

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

        self.register_event(DailyLoginCompletedEvent(
            occurred_at=clock.now(),
            player_id=self.id,
            telegram_id=self.telegram_id,
            earned_xp=earned_xp,
            new_streak=self.daily_streak,
            got_box=got_box
        ))

        return DailyLoginResult(
            earned_xp=earned_xp,
            new_streak=self.daily_streak,
            got_box=got_box,
            already_claimed=False
        )

    def spend_fragments(self, amount: int) -> None:
        self.fragments_balance = self.fragments_balance.spend(amount)

    def spend_xgen(self, amount: int) -> None:
        self.xgen_balance = self.xgen_balance.spend(amount)

    def add_xgen(self, amount: int) -> None:
        self.xgen_balance = self.xgen_balance.add(amount)

    def add_fragments(self, amount: int) -> None:
        self.fragments_balance = self.fragments_balance.add(amount)

    @property
    def level(self) -> int:
        return LevelProgressionService.calculate_level(self.xp)

    def get_max_artifact_slots(self) -> int:
        return LevelProgressionService.get_max_artifact_slots(self.level)


@dataclass
class DailyLoginResult:
    earned_xp: int
    new_streak: int
    got_box: bool = False
    already_claimed: bool = False
