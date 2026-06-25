from datetime import datetime
from dataclasses import dataclass
from uuid import UUID
from enum import Enum


class ExpeditionStatus(str, Enum):
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed" # Время вышло, но лут еще не забран


@dataclass
class Expedition:
    id: UUID
    ship_id: UUID
    zone_id: UUID
    started_at: datetime
    ends_at: datetime
    status: ExpeditionStatus
    