from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID

@dataclass
class Season:
    id: UUID
    name: str
    description: str
    start_date: datetime
    end_date: datetime
    reward_xgen: int = 0
    reward_fragments: int = 0
    is_active: bool = True
    
    def is_currently_active(self) -> bool:
        now = datetime.now(timezone.utc)  # В проде используем UTC!
        return self.is_active and self.start_date <= now <= self.end_date