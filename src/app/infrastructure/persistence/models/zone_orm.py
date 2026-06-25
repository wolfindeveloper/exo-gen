from uuid import UUID
from sqlalchemy import Integer, String, Float, Uuid, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.persistence.models.base import Base


class ZoneORM(Base):
    __tablename__ = "zones"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    image_url: Mapped[str] = mapped_column(String, nullable=False)
    fuel_cost: Mapped[float] = mapped_column(Float, nullable=False)
    optimism_risk: Mapped[float] = mapped_column(Float, nullable=False)
    duration_seconds: Mapped[int] = mapped_column(Integer, nullable=False)
    loot_table: Mapped[list[dict]] = mapped_column(JSONB, nullable=False)