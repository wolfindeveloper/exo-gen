from pydantic import BaseModel

class DailyLoginResponseDTO(BaseModel):
    earned_xp: int
    new_streak: int
    got_box: bool = False
    already_claimed: bool = False   