from dataclasses import dataclass
from uuid import UUID


@dataclass
class StarsPackage:
    id: UUID
    stars_amount: int
    xgen_reward: int
    is_active: bool = True
