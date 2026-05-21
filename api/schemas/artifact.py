"""Pydantic schemas for artifact endpoints."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class ArtifactRead(BaseModel):
    """Single artifact record returned by GET /artifacts."""

    id: str
    slug: str
    recipe_hash: str
    status: str
    cycles_remaining: int
    staked_at: datetime | None = None
    accumulated_yield: float
    bonus_multiplier: float
    domain_slug: str
    created_at: datetime


class StakeResponse(BaseModel):
    """Response for stake/unstake actions."""

    artifact_id: str
    staked: bool
    message: str


class ClaimYieldResponse(BaseModel):
    """Response for claiming staking yield."""

    artifact_id: str
    claimed_amount: float
    new_accumulated: float


class CalibrateResponse(BaseModel):
    """Response for artifact calibration."""

    artifact_id: str
    cycles_remaining: int
    status: str
    xgen_cost: int
    resource_cost_slug: str
