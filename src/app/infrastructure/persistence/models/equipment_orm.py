from uuid import UUID
from typing import TYPE_CHECKING
from sqlalchemy import Uuid, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.persistence.models.base import Base

if TYPE_CHECKING:
    from app.infrastructure.persistence.models.ship_orm import ShipORM


class EquipmentORM(Base):
    __tablename__ = "equipment"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    ship_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("ships.id", ondelete="CASCADE"), unique=True)
    artifacts: Mapped[list[dict]] = mapped_column(JSONB, default=list)

    ship: Mapped["ShipORM"] = relationship(back_populates="equipment")
