from uuid import UUID

from sqlalchemy import String, Uuid, Boolean, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.persistence.models.base import Base


class LootBoxConfigORM(Base):
    __tablename__ = "loot_box_configs"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    box_type: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    entries: Mapped[list[dict]] = mapped_column(JSONB, default=list)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
