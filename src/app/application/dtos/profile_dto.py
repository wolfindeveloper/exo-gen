from pydantic import BaseModel


class ProfileResponseDTO(BaseModel):
    xp: int
    level: int
    total_expeditions: int
    total_artifacts_found: int
    unlocked_articles: int
