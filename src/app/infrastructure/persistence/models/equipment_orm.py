from uuid import UUID
from sqlalchemy import Uuid, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.persistence.models.base import Base


class EquipmentORM(Base):
    __tablename__ = "equipment"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    ship_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("ships.id", ondelete="CASCADE"), unique=True)
    artifacts: Mapped[list[dict]] = mapped_column(JSONB, default=list)
