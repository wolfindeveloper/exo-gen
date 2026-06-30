from datetime import datetime
from uuid import UUID

from sqlalchemy import Integer, String, Uuid, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.persistence.models.base import Base


class StarsPackageORM(Base):
    __tablename__ = "stars_packages"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    stars_amount: Mapped[int] = mapped_column(Integer, nullable=False)
    xgen_reward: Mapped[int] = mapped_column(Integer, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
