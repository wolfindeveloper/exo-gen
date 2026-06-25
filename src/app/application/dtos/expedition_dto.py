from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class StartExpeditionDTO(BaseModel):
    ship_id: UUID
    zone_id: UUID



class ExpeditionResponseDTO(BaseModel):
    id: UUID
    ship_id: UUID
    zone_id: UUID
    started_at: datetime
    ends_at: datetime
    status: str
    remaining_tea: float