from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from app.domain.events.base import DomainEvent


@dataclass(frozen=True)
class PlayerRegisteredEvent(DomainEvent):
    player_id: UUID
    telegram_id: int


@dataclass(frozen=True)
class DailyLoginCompletedEvent(DomainEvent):
    player_id: UUID
    earned_xp: int
    new_streak: int
    got_box: bool


@dataclass(frozen=True)
class ExpeditionStartedEvent(DomainEvent):
    expedition_id: UUID
    ship_id: UUID
    zone_id: UUID
    ends_at: datetime


@dataclass(frozen=True)
class ExpeditionCompletedEvent(DomainEvent):
    expedition_id: UUID
    player_id: UUID
    xgen_earned: int
    fragments_earned: int
    items_earned: list[dict]


@dataclass(frozen=True)
class ArticleUnlockedEvent(DomainEvent):
    player_id: UUID
    article_id: UUID
    chapter_id: UUID


@dataclass(frozen=True)
class ChapterCompletedEvent(DomainEvent):
    player_id: UUID
    chapter_id: UUID
    xgen_rewarded: int
    fragments_rewarded: int
