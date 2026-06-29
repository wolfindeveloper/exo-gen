from dataclasses import dataclass
from datetime import datetime
from uuid import UUID
from enum import Enum


class TransactionStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Transaction:
    id: UUID
    player_id: UUID
    telegram_charge_id: str
    stars_amount: int
    xgen_amount: int
    status: TransactionStatus
    created_at: datetime
