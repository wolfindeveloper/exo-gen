from pydantic import BaseModel
from uuid import UUID

class ClaimExpeditionDTO(BaseModel):
    expedition_id: UUID

class ClaimedItemDTO(BaseModel):
    item_id: UUID
    amount: int
    name: str | None = None

class ClaimExpeditionResponseDTO(BaseModel):
    xgen_earned: int
    fragments_earned: int
    xp_earned: int = 0
    items_earned: list[ClaimedItemDTO] = []
    optimism_lost: float
    current_tea: float
    current_optimism: float