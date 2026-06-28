from dataclasses import dataclass
from uuid import UUID
from datetime import datetime


@dataclass
class UnlockedArticle:
    id: UUID
    player_id: UUID
    article_id: UUID
    unlocked_at: datetime


@dataclass
class ChapterCompletion:
    id: UUID
    """Факт завершения всей главы (все статьи открыты)"""
    player_id: UUID
    chapter_id: UUID
    completed_at: datetime  # Именно это поле пойдет в лидерборд!



@dataclass
class ArticleTriggerProgress:
    id: UUID
    player_id: UUID
    article_id: UUID
    current_count: int = 0

    def increment(self, threshold: int) -> bool:
        self.current_count += 1
        return self.current_count >= threshold