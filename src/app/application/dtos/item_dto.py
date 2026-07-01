from pydantic import BaseModel, ConfigDict
from uuid import UUID
from app.domain.entities.item import ItemType
from app.application.dtos.admin_dto import ItemEffectValidator

class CreateItemDTO(BaseModel):
    name: str
    description: str
    type: ItemType
    rarity: str = "common"
    effect: ItemEffectValidator | None = None
    is_tradable: bool = False
    sell_price: int = 0
    image_url: str = ""

class ItemResponseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    name: str
    description: str
    type: ItemType
    rarity: str
    effect: dict
    is_tradable: bool
    sell_price: int
    image_url: str