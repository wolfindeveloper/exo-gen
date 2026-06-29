from pydantic import BaseModel


class PlayerSettingsDTO(BaseModel):
    language: str
    music_enabled: bool


class UpdatePlayerSettingsDTO(BaseModel):
    language: str | None = None
    music_enabled: bool | None = None
