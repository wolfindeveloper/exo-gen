from uuid import UUID

from pydantic import BaseModel, ConfigDict


class StarsPackageResponseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    stars_amount: int
    xgen_reward: int
    is_active: bool


class BuyXgenRequestDTO(BaseModel):
    package_id: UUID


class BuyXgenResponseDTO(BaseModel):
    invoice_url: str
    package_id: UUID
