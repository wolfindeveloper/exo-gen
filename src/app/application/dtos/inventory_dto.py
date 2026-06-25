from pydantic import BaseModel, ConfigDict
from uuid import UUID
from app.application.dtos.item_dto import ItemResponseDTO

class InventoryItemDTO(BaseModel):
    item: ItemResponseDTO  # Полная информация о предмете из справочника
    quantity: int          # Сколько штук в рюкзаке

class InventoryResponseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    items: list[InventoryItemDTO]

class UseItemDTO(BaseModel):
    item_id: UUID      # ID предмета из глобального справочника (Item)
    ship_id: UUID      # ID корабля, к которому применяем расходник

class UseItemResponseDTO(BaseModel):
    message: str
    new_tea_level: float
    new_optimism: float