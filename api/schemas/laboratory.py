"""Pydantic schemas for laboratory endpoints."""

from __future__ import annotations

from pydantic import BaseModel, Field


class CraftRequest(BaseModel):
    """Request body for POST /laboratory/craft."""

    domain_slug: str = Field(min_length=1, description="Galaxy zone slug for crafting")
    essences: list[str] = Field(
        min_length=3,
        max_length=5,
        description="List of 3-5 essence slugs to combine",
    )
    xgen_amount: int = Field(ge=0, description="$XGEN amount to burn (100% burned)")


class CraftResponse(BaseModel):
    """Response for craft attempt."""

    status: str = Field(description="'created' or 'taken'")
    recipe_hash: str
    artifact_id: str | None = None
    essences_refunded: list[str] | None = None
    xgen_burned: int


class RecipeInfo(BaseModel):
    """Public recipe info for GET /laboratory/recipes/{hash}."""

    recipe_hash: str
    artifact_slug: str
    domain_slug: str
    essence_count: int
    created_at: str
