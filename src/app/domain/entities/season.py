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
    deleted_at: datetime | None = None

    def update(
        self,
        name: str | None = None,
        description: str | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        reward_xgen: int | None = None,
        reward_fragments: int | None = None,
        is_active: bool | None = None,
    ) -> None:
        if name is not None:
            self.name = name
        if description is not None:
            self.description = description
        if start_date is not None:
            self.start_date = start_date
        if end_date is not None:
            self.end_date = end_date
        if reward_xgen is not None:
            self.reward_xgen = reward_xgen
        if reward_fragments is not None:
            self.reward_fragments = reward_fragments
        if is_active is not None:
            self.is_active = is_active

    def soft_delete(self) -> None:
        self.deleted_at = datetime.now(timezone.utc)

    def is_deleted(self) -> bool:
        return self.deleted_at is not None

    def is_currently_active(self) -> bool:
        now = datetime.now(timezone.utc)
        return self.is_active and self.start_date <= now <= self.end_date