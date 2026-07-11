from uuid import uuid4

import pytest

from app.domain.entities.equipment import Equipment
from app.domain.value_objects.equipment import SlotType
from app.domain.exceptions.equipment import ArtifactAlreadyEquippedError


class TestEquipmentDomain:
    def test_equip_adds_artifact(self):
        equipment = Equipment(ship_id=uuid4())
        item_id = uuid4()

        result = equipment.equip(item_id, SlotType.SPEED, {"speed": 0.1})

        assert result is None
        assert len(equipment.artifacts) == 1
        assert equipment.artifacts[0].item_id == item_id
        assert equipment.artifacts[0].slot_type == SlotType.SPEED

    def test_equip_duplicate_raises_error(self):
        equipment = Equipment(ship_id=uuid4())
        item_id = uuid4()

        equipment.equip(item_id, SlotType.LUCK, {"luck": 0.05})

        with pytest.raises(ArtifactAlreadyEquippedError, match="already equipped"):
            equipment.equip(item_id, SlotType.DEFENSE, {"defense": 0.1})

    def test_equip_replaces_existing_artifact_on_same_slot(self):
        equipment = Equipment(ship_id=uuid4())
        item_id_1 = uuid4()
        item_id_2 = uuid4()

        result_1 = equipment.equip(item_id_1, SlotType.SPEED, {"speed": 0.1})
        assert result_1 is None
        assert len(equipment.artifacts) == 1

        result_2 = equipment.equip(item_id_2, SlotType.SPEED, {"speed": 0.2})
        assert result_2 is not None
        assert result_2.item_id == item_id_1
        assert len(equipment.artifacts) == 1
        assert equipment.artifacts[0].item_id == item_id_2
        assert equipment.artifacts[0].slot_type == SlotType.SPEED

    def test_equip_empty_slot_returns_none(self):
        equipment = Equipment(ship_id=uuid4())

        result = equipment.equip(uuid4(), SlotType.SPEED, {"speed": 0.1})
        assert result is None

    def test_unequip_removes_artifact(self):
        equipment = Equipment(ship_id=uuid4())
        item_id = uuid4()

        equipment.equip(item_id, SlotType.SPEED, {"speed": 0.1})
        removed = equipment.unequip(item_id)

        assert len(equipment.artifacts) == 0
        assert removed.item_id == item_id

    def test_unequip_nonexistent_raises_error(self):
        equipment = Equipment(ship_id=uuid4())

        with pytest.raises(ValueError, match="not equipped"):
            equipment.unequip(uuid4())

    def test_get_total_bonuses_empty(self):
        equipment = Equipment(ship_id=uuid4())

        assert equipment.get_total_bonuses() == {}

    def test_get_total_bonuses_different_slots(self):
        equipment = Equipment(ship_id=uuid4())

        equipment.equip(uuid4(), SlotType.SPEED, {"speed": 0.1})
        equipment.equip(uuid4(), SlotType.LUCK, {"luck": 0.05})

        bonuses = equipment.get_total_bonuses()
        assert bonuses["speed"] == 0.1
        assert bonuses["luck"] == 0.05

    def test_get_total_bonuses_replaces_on_same_slot(self):
        equipment = Equipment(ship_id=uuid4())

        equipment.equip(uuid4(), SlotType.SPEED, {"speed": 0.1})
        equipment.equip(uuid4(), SlotType.SPEED, {"speed": 0.15})

        bonuses = equipment.get_total_bonuses()
        assert bonuses["speed"] == 0.15

    def test_get_total_bonuses_multiple_keys_per_artifact(self):
        equipment = Equipment(ship_id=uuid4())

        equipment.equip(uuid4(), SlotType.LUCK, {"luck": 0.05, "speed": 0.02})

        bonuses = equipment.get_total_bonuses()
        assert bonuses["luck"] == 0.05
        assert bonuses["speed"] == 0.02

    def test_unequip_returns_correct_artifact(self):
        equipment = Equipment(ship_id=uuid4())
        item_id_1 = uuid4()
        item_id_2 = uuid4()

        equipment.equip(item_id_1, SlotType.SPEED, {"speed": 0.1})
        equipment.equip(item_id_2, SlotType.LUCK, {"luck": 0.05})

        removed = equipment.unequip(item_id_1)
        assert removed.item_id == item_id_1
        assert len(equipment.artifacts) == 1
        assert equipment.artifacts[0].item_id == item_id_2

    def test_equip_multiple_artifacts_same_item_id_different_slot(self):
        equipment = Equipment(ship_id=uuid4())
        item_id = uuid4()

        equipment.equip(item_id, SlotType.SPEED, {"speed": 0.1})

        with pytest.raises(ArtifactAlreadyEquippedError, match="already equipped"):
            equipment.equip(item_id, SlotType.LUCK, {"luck": 0.05})
