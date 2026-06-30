import logging
from random import SystemRandom

_rng = SystemRandom()
logger = logging.getLogger(__name__)


def generate_loot(loot_table: list[dict]) -> dict:
    rewards = {"xgen": 0, "fragments": 0, "items": []}

    for entry in loot_table:
        if _rng.random() < entry.get("chance", 0):
            item_type = entry.get("item_type")

            if item_type == "xgen":
                rewards["xgen"] += entry.get("amount", 0)
            elif item_type == "fragments":
                rewards["fragments"] += entry.get("amount", 0)
            elif item_type == "item":
                item_id = entry.get("item_id")
                if item_id:
                    rewards["items"].append({
                        "item_id": item_id,
                        "amount": entry.get("amount", 1)
                    })
                else:
                    logger.warning(f"В зоне найден предмет без item_id: {entry}")

    return rewards