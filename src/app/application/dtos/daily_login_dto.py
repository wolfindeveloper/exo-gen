from pydantic import BaseModel


class DailyLoginResponseDTO(BaseModel):
    earned_xp: int
    new_streak: int
    got_box: bool = False
    already_claimed: bool = False
    box_opened: bool = False
    box_xgen: int = 0
    box_fragments: int = 0
    box_items: list[dict] = []
