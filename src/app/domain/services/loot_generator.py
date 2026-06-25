import random

def generate_loot(loot_table: list[dict]) -> dict:
    rewards = {"xgen": 0, "fragments": 0, "items": []}

    for entry in loot_table:
        # .get("chance", 0) - если chance нет, шанс будет 0
        if random.random() < entry.get("chance", 0):
            item_type = entry.get("item_type")
            
            if item_type == "xgen":
                rewards["xgen"] += entry.get("amount", 0)
            elif item_type == "fragments":
                rewards["fragments"] += entry.get("amount", 0)
            elif item_type == "item":
                item_id = entry.get("item_id")
                # ЗАЩИТА: Добавляем предмет только если item_id реально указан
                if item_id:
                    rewards["items"].append({
                        "item_id": item_id,
                        "amount": entry.get("amount", 1)
                    })
                else:
                    # В продакшене здесь был бы вызов логгера (logger.warning)
                    print(f"⚠️ WARNING: В зоне найден предмет без item_id: {entry}")
                
    return rewards