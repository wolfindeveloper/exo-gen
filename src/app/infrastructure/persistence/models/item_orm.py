from uuid import UUID
from sqlalchemy import String, Uuid, Text, Boolean, Integer
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.persistence.models.base import Base

class ItemORM(Base):
    __tablename__ = "items"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Enum в Python, но в БД храним как строку (так надежнее для миграций)
    type: Mapped[str] = mapped_column(String(50), nullable=False) 
    rarity: Mapped[str] = mapped_column(String(50), default="common")
    
    # JSONB для гибких эффектов
    effect: Mapped[dict] = mapped_column(JSONB, default=dict)
    
    is_tradable: Mapped[bool] = mapped_column(Boolean, default=False)
    sell_price: Mapped[int] = mapped_column(Integer, default=0)