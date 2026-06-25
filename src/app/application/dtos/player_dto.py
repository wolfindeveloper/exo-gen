from pydantic import BaseModel

class CreatePlayerDTO(BaseModel):
    telegram_id: int
    username: str | None = None