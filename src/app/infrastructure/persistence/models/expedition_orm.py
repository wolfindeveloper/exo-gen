from uuid import UUID
from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import String, Uuid, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.persistence.models.base import Base

if TYPE_CHECKING:
    from app.infrastructure.persistence.models.ship_orm import ShipORM




class ExpeditionORM(Base):
    __tablename__ = "expeditions"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, index=True)
    ship_id: Mapped[UUID] = mapped_column(ForeignKey("ships.id"))
    zone_id: Mapped[UUID] = mapped_column(ForeignKey("zones.id"))
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    ends_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(50), nullable=False)

    ship: Mapped["ShipORM"] = relationship(back_populates="expeditions")