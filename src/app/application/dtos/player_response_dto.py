from pydantic import BaseModel
from uuid import UUID


class PlayerResponseDTO(BaseModel):
    id: UUID
    telegram_id: int
    username: str | None
    xp: int
    xgen_balance: int
    fragments_balance: int
    daily_streak: int
    ship_count: int 
    ship_id: UUID