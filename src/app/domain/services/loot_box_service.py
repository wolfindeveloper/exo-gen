import logging
from random import SystemRandom, Random
from dataclasses import dataclass, field

from app.domain.entities.loot_box_config import LootBoxConfig

logger = logging.getLogger(__name__)


@dataclass
class GeneratedLoot:
    xgen: int = 0
    fragments: int = 0
    items: list[dict] = field(default_factory=list)


class LootBoxService:
    def __init__(self, rng: Random | None = None) -> None:
        self._rng = rng or SystemRandom()

    def generate(self, config: LootBoxConfig) -> GeneratedLoot:
        loot = GeneratedLoot()

        for entry in config.entries:
            if self._rng.random() < entry.chance:
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
