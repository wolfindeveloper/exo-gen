from uuid import uuid4
from random import Random

from app.domain.entities.loot_box_config import LootBoxConfig
from app.domain.services.loot_box_service import LootBoxService, GeneratedLoot
from app.domain.value_objects.loot_box import LootBoxType, LootBoxEntry


class TestLootBoxService:
    def test_generate_xgen_only(self):
        service = LootBoxService(rng=Random(42))
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

        loot = service.generate(config)

        assert loot.xgen > 0
        assert loot.fragments == 0
        assert loot.items == []

    def test_generate_with_items(self):
        service = LootBoxService(rng=Random(7))
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

        loot = service.generate(config)

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

        loot_a = LootBoxService(rng=Random(123)).generate(config)
        loot_b = LootBoxService(rng=Random(123)).generate(config)

        assert loot_a.xgen == loot_b.xgen
        assert loot_a.fragments == loot_b.fragments

    def test_generate_empty_config(self):
        service = LootBoxService(rng=Random(0))
        config = LootBoxConfig(
            id=uuid4(),
            box_type=LootBoxType.CHAPTER_REWARD,
            name="Empty Box",
            description="Nothing inside",
            entries=[],
        )

        loot = service.generate(config)

        assert isinstance(loot, GeneratedLoot)
        assert loot.xgen == 0
        assert loot.fragments == 0
        assert loot.items == []
