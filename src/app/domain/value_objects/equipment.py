from enum import Enum


class SlotType(str, Enum):
    SPEED = "speed"
    DEFENSE = "defense"
    CAPACITY = "capacity"
    LUCK = "luck"
    FUEL_EFFICIENCY = "fuel"
    REPAIR_EFFICIENCY = "repair"
    XP_BOOST = "xp"
    FRAGMENT_BOOST = "fragment"
