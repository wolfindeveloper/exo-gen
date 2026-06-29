from uuid import uuid4

from app.domain.entities.item import Item, ItemType
from app.domain.services.consumable_selector import ConsumableSelector


def make_item(item_id, effect_key, effect_value):
    return Item(
        id=item_id,
        name="Test Consumable",
        description="Test",
        type=ItemType.CONSUMABLE,
        effect={effect_key: effect_value},
    )


class TestConsumableSelector:
    def setup_method(self):
        self.selector = ConsumableSelector()

    def test_select_minimal_sufficient_consumable(self):
        small_id = uuid4()
        medium_id = uuid4()
        large_id = uuid4()

        items = [
            (make_item(small_id, "restore_tea", 20.0), 5),
            (make_item(medium_id, "restore_tea", 50.0), 3),
            (make_item(large_id, "restore_tea", 100.0), 1),
        ]

        decision = self.selector.select_for_refuel(
            available_items=items,
            current_tea=70.0,
            max_tea=100.0,
        )

        assert decision.chosen_item is not None
        assert decision.chosen_item.id == medium_id
        assert decision.reason == "minimal_sufficient"

    def test_select_maximal_when_none_covers_deficit(self):
        small_id = uuid4()
        medium_id = uuid4()

        items = [
            (make_item(small_id, "restore_tea", 20.0), 5),
            (make_item(medium_id, "restore_tea", 30.0), 3),
        ]

        decision = self.selector.select_for_refuel(
            available_items=items,
            current_tea=20.0,
            max_tea=100.0,
        )

        assert decision.chosen_item is not None
        assert decision.chosen_item.id == medium_id
        assert decision.reason == "maximal_available"

    def test_returns_none_when_no_consumables(self):
        decision = self.selector.select_for_refuel(
            available_items=[],
            current_tea=50.0,
        )

        assert decision.chosen_item is None
        assert decision.reason == "no_consumables"

    def test_respects_inventory_quantity(self):
        small_id = uuid4()
        large_id = uuid4()

        items = [
            (make_item(small_id, "restore_tea", 20.0), 0),
            (make_item(large_id, "restore_tea", 100.0), 5),
        ]

        decision = self.selector.select_for_refuel(
            available_items=items,
            current_tea=90.0,
            max_tea=100.0,
        )

        assert decision.chosen_item is not None
        assert decision.chosen_item.id == large_id
        assert decision.reason == "minimal_sufficient"

    def test_select_for_repair_same_logic(self):
        small_id = uuid4()
        medium_id = uuid4()

        items = [
            (make_item(small_id, "restore_optimism", 20.0), 2),
            (make_item(medium_id, "restore_optimism", 50.0), 2),
        ]

        decision = self.selector.select_for_repair(
            available_items=items,
            current_optimism=60.0,
            max_optimism=100.0,
        )

        assert decision.chosen_item is not None
        assert decision.chosen_item.id == medium_id
        assert decision.reason == "minimal_sufficient"

    def test_repair_selects_maximal_when_none_covers(self):
        small_id = uuid4()

        items = [
            (make_item(small_id, "restore_optimism", 10.0), 1),
        ]

        decision = self.selector.select_for_repair(
            available_items=items,
            current_optimism=5.0,
            max_optimism=100.0,
        )

        assert decision.chosen_item is not None
        assert decision.chosen_item.id == small_id
        assert decision.reason == "maximal_available"

    def test_repair_returns_none_when_no_consumables(self):
        decision = self.selector.select_for_repair(
            available_items=[],
            current_optimism=50.0,
        )

        assert decision.chosen_item is None
        assert decision.reason == "no_consumables"
