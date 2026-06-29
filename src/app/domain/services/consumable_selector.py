from dataclasses import dataclass

from app.domain.entities.item import Item


@dataclass(frozen=True)
class ConsumptionDecision:
    chosen_item: Item | None
    reason: str


class ConsumableSelector:
    def select_for_refuel(
        self,
        available_items: list[tuple[Item, int]],
        current_tea: float,
        max_tea: float = 100.0,
        effect_key: str = "restore_tea",
    ) -> ConsumptionDecision:
        return self._select(
            available_items=available_items,
            current_value=current_tea,
            max_value=max_tea,
            effect_key=effect_key,
        )

    def select_for_repair(
        self,
        available_items: list[tuple[Item, int]],
        current_optimism: float,
        max_optimism: float = 100.0,
        effect_key: str = "restore_optimism",
    ) -> ConsumptionDecision:
        return self._select(
            available_items=available_items,
            current_value=current_optimism,
            max_value=max_optimism,
            effect_key=effect_key,
        )

    def _select(
        self,
        available_items: list[tuple[Item, int]],
        current_value: float,
        max_value: float,
        effect_key: str,
    ) -> ConsumptionDecision:
        valid = [
            (item, qty)
            for item, qty in available_items
            if qty > 0 and effect_key in item.effect
        ]
        if not valid:
            return ConsumptionDecision(None, "no_consumables")

        deficit = max_value - current_value
        sorted_by_effect = sorted(valid, key=lambda x: float(x[0].effect[effect_key]))

        for item, _ in sorted_by_effect:
            if float(item.effect[effect_key]) >= deficit:
                return ConsumptionDecision(item, "minimal_sufficient")

        best = sorted_by_effect[-1][0]
        return ConsumptionDecision(best, "maximal_available")
