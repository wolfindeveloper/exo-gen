from pydantic import BaseModel


class ProfileResponseDTO(BaseModel):
    xp: int
    level: int
    total_expeditions: int
    total_artifacts_found: int
    unlocked_articles: int
    expeditions_completed: int
    expeditions_in_progress: int = 0
    artifacts_found: int
    xgen_earned_total: int
    articles_read: int
    articles_total: int = 0
