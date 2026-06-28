from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, ConfigDict


# --- DTO для создания (Запросы) ---


class CreateArticleDTO(BaseModel):
    chapter_id: UUID | None = None
    title: str
    content: str
    fragment_cost: int = 0
    trigger_event_type: str | None = None
    trigger_threshold: int = 1


class CreateChapterDTO(BaseModel):
    name: str
    description: str
    is_secret: bool
    season_id: UUID | None = None
    reward_xgen: int = 0
    reward_fragments: int = 0
    # В Pydantic V2 безопасно использовать просто []
    articles: list[CreateArticleDTO] = []


class CreateSeasonDTO(BaseModel):
    name: str
    description: str
    start_date: datetime
    end_date: datetime
    reward_xgen: int = 0
    reward_fragments: int = 0
    is_active: bool = True


# --- DTO для ответа (Ответы) ---


class ArticleResponseDTO(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )  # Позволяет читать атрибуты ORM/dataclass

    id: UUID
    chapter_id: UUID
    title: str
    content: str | None = None
    is_unlocked: bool = False
    fragment_cost: int = 0
    trigger_event_type: str | None = None
    trigger_threshold: int = 1


class ChapterResponseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    description: str
    is_secret: bool
    season_id: UUID | None = None
    reward_xgen: int = 0
    reward_fragments: int = 0
    articles: list[ArticleResponseDTO] = []


class SeasonResponseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    description: str
    start_date: datetime
    end_date: datetime
    reward_xgen: int = 0
    reward_fragments: int = 0
    is_active: bool = True


class GuideResponseDTO(BaseModel):
    chapters: list[ChapterResponseDTO]
    player_fragments_balance: int  # Фронт сразу знает, хватает ли валюты


class UnlockArticleDTO(BaseModel):
    article_id: UUID


class UnlockArticleResponseDTO(BaseModel):
    content: str
    new_fragments_balance: int
    chapter_completed: bool
    xgen_rewarded: int
    fragments_rewarded: int = 0
    box_opened: bool = False
    box_xgen: int = 0
    box_fragments: int = 0
    box_items: list[dict] = []


class TriggerEventDTO(BaseModel):
    event_type: str


class TriggerEventResponseDTO(BaseModel):
    newly_unlocked_articles: list[str]  # Список названий (title)
    box_opened: bool = False
    box_xgen: int = 0
    box_fragments: int = 0
    box_items: list[dict] = []


class LeaderboardEntryDTO(BaseModel):
    username: str
    chapter_name: str
    completed_at: datetime
