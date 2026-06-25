from pydantic import BaseModel

class CreatePlayerDTO(BaseModel):
    username: str | None = None