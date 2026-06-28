from datetime import datetime, timezone
from dataclasses import dataclass
from uuid import UUID
from enum import Enum

from app.domain.entities.base import AggregateRoot
from app.domain.events.player_events import ExpeditionCompletedEvent


class ExpeditionStatus(str, Enum):
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


@dataclass
class Expedition(AggregateRoot):
    id: UUID
    ship_id: UUID
    zone_id: UUID
    started_at: datetime
    ends_at: datetime
    status: ExpeditionStatus

    def complete(self, player_id: UUID, telegram_id: int, xgen_earned: int, fragments_earned: int, items_earned: list[dict]) -> None:
        self.status = ExpeditionStatus.COMPLETED
        self.register_event(ExpeditionCompletedEvent(
            occurred_at=datetime.now(timezone.utc),
            expedition_id=self.id,
            player_id=player_id,
            telegram_id=telegram_id,
            xgen_earned=xgen_earned,
            fragments_earned=fragments_earned,
            items_earned=items_earned
        ))
