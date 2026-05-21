"""SQLAlchemy ORM models for EXO GENESIS."""

from datetime import datetime, timezone

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    Float,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class Player(Base):
    __tablename__ = "players"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    username: Mapped[str] = mapped_column(String(64), nullable=False)
    level: Mapped[int] = mapped_column(Integer, default=1)
    xp: Mapped[int] = mapped_column(Integer, default=0)
    tier: Mapped[int] = mapped_column(Integer, default=1)
    xgen_balance: Mapped[int] = mapped_column(BigInteger, default=0)
    verification_status: Mapped[str] = mapped_column(String(16), default="none")
    language: Mapped[str] = mapped_column(String(4), default="en")
    avatar_slug: Mapped[str | None] = mapped_column(String(64), nullable=True)
    notifications_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    weekly_expeditions: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, onupdate=_utcnow)


class Ship(Base):
    __tablename__ = "ships"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    player_id: Mapped[str] = mapped_column(String(36), nullable=False)
    slug: Mapped[str] = mapped_column(String(64), nullable=False)
    stability: Mapped[int] = mapped_column(Integer, default=100)
    is_nft: Mapped[bool] = mapped_column(Boolean, default=False)
    is_staked: Mapped[bool] = mapped_column(Boolean, default=False)
    in_repair: Mapped[bool] = mapped_column(Boolean, default=False)
    repair_mode: Mapped[str | None] = mapped_column(String(16), nullable=True)
    repair_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    expedition_cycles: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)


class Expedition(Base):
    __tablename__ = "expeditions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    player_id: Mapped[str] = mapped_column(String(36), nullable=False)
    ship_id: Mapped[str] = mapped_column(String(36), nullable=False)
    slug: Mapped[str] = mapped_column(String(64), nullable=False)
    tier: Mapped[int] = mapped_column(Integer, nullable=False)
    overdrive_mode: Mapped[str] = mapped_column(String(16), default="stable")
    status: Mapped[str] = mapped_column(String(16), default="pending")
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    estimated_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    loot: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    xp_reward: Mapped[int] = mapped_column(Integer, default=0)
    damage_occurred: Mapped[bool] = mapped_column(Boolean, default=False)


class Artifact(Base):
    __tablename__ = "artifacts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    player_id: Mapped[str] = mapped_column(String(36), nullable=False)
    slug: Mapped[str] = mapped_column(String(64), nullable=False)
    recipe_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    status: Mapped[str] = mapped_column(String(16), default="active")
    cycles_remaining: Mapped[int] = mapped_column(Integer, default=10)
    staked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_yield_claim: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    accumulated_yield: Mapped[float] = mapped_column(Float, default=0.0)
    bonus_multiplier: Mapped[float] = mapped_column(Float, default=1.0)
    domain_slug: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)


class PlayerInventory(Base):
    __tablename__ = "player_inventory"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    player_id: Mapped[str] = mapped_column(String(36), nullable=False)
    slug: Mapped[str] = mapped_column(String(64), nullable=False)
    quantity: Mapped[int] = mapped_column(BigInteger, default=0)


class XgenTransaction(Base):
    __tablename__ = "xgen_transactions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    player_id: Mapped[str] = mapped_column(String(36), nullable=False)
    amount: Mapped[int] = mapped_column(BigInteger, nullable=False)
    direction: Mapped[str] = mapped_column(String(8), nullable=False)
    reason: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
