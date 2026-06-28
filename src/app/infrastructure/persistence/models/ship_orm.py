from uuid import UUID
from typing import TYPE_CHECKING
from sqlalchemy import String, Float, ForeignKey, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.persistence.models.base import Base

if TYPE_CHECKING:
    from app.infrastructure.persistence.models.player_orm import PlayerORM
    from app.infrastructure.persistence.models.expedition_orm import ExpeditionORM
    from app.infrastructure.persistence.models.equipment_orm import EquipmentORM

class ShipORM(Base):
    __tablename__ = "ships"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, index=True)
    player_id: Mapped[UUID] = mapped_column(ForeignKey("players.id"))
    name: Mapped[str] = mapped_column(String(30), default="Vogon MK")
    tea_level: Mapped[float] = mapped_column(Float, default="100.0")
    optimism: Mapped[float] = mapped_column(Float, default="100.0")
    speed: Mapped[float] = mapped_column(Float, default="1.0")
    defense: Mapped[float] = mapped_column(Float, default="0.0")
    luck: Mapped[float] = mapped_column(Float, default="0.0")

    player: Mapped["PlayerORM"] = relationship(back_populates="ships")
    expeditions: Mapped[list["ExpeditionORM"]] = relationship(back_populates="ship")
    equipment: Mapped["EquipmentORM | None"] = relationship(
        back_populates="ship",
        uselist=False,
        cascade="all, delete-orphan",
    )