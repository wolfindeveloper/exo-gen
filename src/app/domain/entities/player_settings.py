from dataclasses import dataclass
from uuid import UUID


@dataclass
class PlayerSettings:
    player_id: UUID
    language: str = "en"
    music_enabled: bool = True
