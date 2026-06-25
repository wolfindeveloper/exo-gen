from uuid import UUID
from sqlalchemy import Integer, Uuid, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.persistence.models.base import Base

class InventoryItemORM(Base):
    __tablename__ = "inventory_items"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    
    # CASCADE означает: если удалят игрока или предмет из справочника, 
    # эта запись из инвентаря удалится автоматически.
    player_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("players.id", ondelete="CASCADE"), nullable=False)
    item_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("items.id", ondelete="CASCADE"), nullable=False)
    
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    
    # Обходим зарезервированное слово 'metadata'
    item_metadata: Mapped[dict] = mapped_column("metadata", JSONB, default=dict)