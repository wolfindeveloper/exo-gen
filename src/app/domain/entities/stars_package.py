from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID


@dataclass
class StarsPackage:
    id: UUID
    stars_amount: int
    xgen_reward: int
    is_active: bool = True
    deleted_at: datetime | None = None

    def update(
        self,
        stars_amount: int | None = None,
        xgen_reward: int | None = None,
        is_active: bool | None = None,
    ) -> None:
        if stars_amount is not None:
            self.stars_amount = stars_amount
        if xgen_reward is not None:
            self.xgen_reward = xgen_reward
        if is_active is not None:
            self.is_active = is_active

    def soft_delete(self) -> None:
        self.deleted_at = datetime.now(timezone.utc)

    def is_deleted(self) -> bool:
        return self.deleted_at is not None
