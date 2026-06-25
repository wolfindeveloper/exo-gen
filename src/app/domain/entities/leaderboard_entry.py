from dataclasses import dataclass
from datetime import datetime


@dataclass
class LeaderboardEntry:
    username: str
    chapter_name: str
    completed_at: datetime