import logging
import random
from dataclasses import dataclass, field

from app.domain.entities.loot_box_config import LootBoxConfig

logger = logging.getLogger(__name__)


@dataclass
class GeneratedLoot:
    xgen: int = 0
    fragments: int = 0
    items: list[dict] = field(default_factory=list)


class LootBoxService:
    def generate(self, config: LootBoxConfig, seed: int | None = None) -> GeneratedLoot:
        if seed is not None:
            random.seed(seed)

        loot = GeneratedLoot()

        for entry in config.entries:
            if random.random() < entry.chance:
                if entry.item_type == "xgen":
                    loot.xgen += entry.amount
                elif entry.item_type == "fragments":
                    loot.fragments += entry.amount
                elif entry.item_type == "item":
                    if entry.item_id:
                        loot.items.append(
                            {
                                "item_id": str(entry.item_id),
                                "amount": entry.amount,
                            }
                        )
                    else:
                        logger.warning(f"LootBox entry without item_id: {entry}")

        return loot
