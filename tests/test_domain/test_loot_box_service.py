from uuid import uuid4

from app.domain.entities.loot_box_config import LootBoxConfig
from app.domain.services.loot_box_service import LootBoxService, GeneratedLoot
from app.domain.value_objects.loot_box import LootBoxType, LootBoxEntry


class TestLootBoxService:
    def setup_method(self):
        self.service = LootBoxService()

    def test_generate_xgen_only(self):
        config = LootBoxConfig(
            id=uuid4(),
            box_type=LootBoxType.WELCOME,
            name="Welcome Box",
            description="Starter box",
            entries=[
                LootBoxEntry(item_type="xgen", amount=100, chance=1.0),
                LootBoxEntry(item_type="xgen", amount=50, chance=0.5),
            ],
        )

        loot = self.service.generate(config, seed=42)

        assert loot.xgen > 0
        assert loot.fragments == 0
        assert loot.items == []

    def test_generate_with_items(self):
        item_id = uuid4()
        config = LootBoxConfig(
            id=uuid4(),
            box_type=LootBoxType.SHOP,
            name="Lucky Box",
            description="Contains random items",
            entries=[
                LootBoxEntry(item_type="item", amount=1, chance=1.0, item_id=item_id),
                LootBoxEntry(item_type="item", amount=3, chance=1.0, item_id=item_id),
            ],
        )

        loot = self.service.generate(config, seed=7)

        assert loot.xgen == 0
        assert loot.fragments == 0
        assert len(loot.items) > 0
        for entry in loot.items:
            assert "item_id" in entry
            assert "amount" in entry

    def test_generate_with_seed_deterministic(self):
        config = LootBoxConfig(
            id=uuid4(),
            box_type=LootBoxType.DAILY_42,
            name="Daily Box",
            description="42-day streak reward",
            entries=[
                LootBoxEntry(item_type="xgen", amount=500, chance=0.8),
                LootBoxEntry(item_type="fragments", amount=10, chance=0.3),
            ],
        )

        loot_a = self.service.generate(config, seed=123)
        loot_b = self.service.generate(config, seed=123)

        assert loot_a.xgen == loot_b.xgen
        assert loot_a.fragments == loot_b.fragments

    def test_generate_empty_config(self):
        config = LootBoxConfig(
            id=uuid4(),
            box_type=LootBoxType.CHAPTER_REWARD,
            name="Empty Box",
            description="Nothing inside",
            entries=[],
        )

        loot = self.service.generate(config, seed=0)

        assert isinstance(loot, GeneratedLoot)
        assert loot.xgen == 0
        assert loot.fragments == 0
        assert loot.items == []
