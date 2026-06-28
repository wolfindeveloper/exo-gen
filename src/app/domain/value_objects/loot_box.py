from dataclasses import dataclass
from enum import Enum
from uuid import UUID


class LootBoxType(str, Enum):
    WELCOME = "welcome"
    DAILY_42 = "daily_42"
    CHAPTER_REWARD = "chapter_reward"
    SHOP = "shop"


@dataclass(frozen=True)
class LootBoxEntry:
    item_type: str
    amount: int
    chance: float
    item_id: UUID | None = None
