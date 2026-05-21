"""Pydantic schemas for expedition endpoints."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class ExpeditionStartRequest(BaseModel):
    """Request body for POST /expeditions/start."""

    ship_slug: str = Field(min_length=1, description="Slug of the ship to send")
    tier: int = Field(ge=1, le=5, description="Expedition tier (1-5)")
    fuel_slug: str = Field(min_length=1, description="Primary fuel slug")
    overdrive_mode: str = Field(
        default="stable",
        pattern="^(stable|push|overdrive)$",
        description="Overdrive protocol mode",
    )


class ExpeditionRead(BaseModel):
    """Single expedition record returned by GET /expeditions/{id}."""

    id: str
    ship_id: str
    slug: str
    tier: int
    overdrive_mode: str
    status: str
    started_at: datetime
    estimated_end: datetime
    completed_at: datetime | None = None
    loot: dict | None = None
    xp_reward: int
    damage_occurred: bool


class ActiveExpeditionRead(BaseModel):
    """Summary of an active expedition for list view."""

    id: str
    slug: str
    tier: int
    overdrive_mode: str
    status: str
    started_at: datetime
    estimated_end: datetime
    progress_percent: float = Field(description="Completion percentage 0-100")
