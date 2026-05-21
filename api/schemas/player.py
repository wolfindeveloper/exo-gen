"""Pydantic schemas for player-related endpoints."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class PlayerRead(BaseModel):
    """Read-only player profile returned by GET /player/me."""

    id: str = Field(description="Unique player identifier (UUID)")
    telegram_id: int = Field(description="Telegram user ID")
    username: str = Field(description="Display name (Telegram or custom)")
    level: int = Field(ge=1, le=100, description="Current player level (1-100)")
    xp: int = Field(ge=0, description="Accumulated experience points")
    tier: int = Field(ge=1, le=5, description="Fuel tier access level (1-5)")
    xgen_balance: int = Field(ge=0, description="$XGEN token balance")
    verification_status: Literal["none", "basic", "verified"] = Field(
        description="Identity verification level"
    )


class PlayerUpdate(BaseModel):
    """Fields that a player can update via PATCH /player/me."""

    username: str | None = Field(
        default=None,
        min_length=2,
        max_length=32,
        description="Custom display name",
    )
    language: Literal["ru", "en", "la"] | None = Field(
        default=None,
        description="Preferred interface language",
    )
    avatar_slug: str | None = Field(
        default=None,
        description="Selected avatar slug from config/avatars.json",
    )
    notifications_enabled: bool | None = Field(
        default=None,
        description="Toggle push notifications",
    )
