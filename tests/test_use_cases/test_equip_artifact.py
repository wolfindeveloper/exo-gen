from unittest.mock import MagicMock, AsyncMock
from uuid import uuid4

import pytest

from app.application.use_cases.equip_artifact import EquipArtifactUseCase
from app.application.use_cases.unequip_artifact import UnequipArtifactUseCase
from app.application.dtos.equipment_dto import EquipArtifactDTO, UnequipArtifactDTO
from app.domain.entities.player import Player
from app.domain.entities.ship import Ship
from app.domain.entities.item import Item, ItemType
from app.domain.entities.equipment import Equipment
from app.domain.value_objects.resources import TeaLevel, Optimism, XgenBalance, FragmentsBalance
from app.domain.value_objects.equipment import SlotType
from app.domain.repositories.equipment_repository import EquipmentRepository
from app.domain.exceptions.ship import ShipNotFoundError
from app.domain.exceptions.inventory import ItemNotFoundError, ItemNotInInventoryError


TG_ID = 12345
PLAYER_USERNAME = "arthur"


def make_player(player_id, ships=None):
    return Player(
        id=player_id,
        telegram_id=TG_ID,
        username=PLAYER_USERNAME,
        xp=0,
        xgen_balance=XgenBalance(0),
        fragments_balance=FragmentsBalance(0),
        daily_streak=0,
        last_login_date=None,
        ships=ships or [],
    )


def make_ship(ship_id, player_id):
    return Ship(
        id=ship_id,
        player_id=player_id,
        name="Test Ship",
        tea_level=TeaLevel(100.0),
        optimism=Optimism(100.0),
        speed=1.0,
        defense=0.0,
        luck=0.0,
    )


def make_artifact(item_id, effect=None):
    return Item(
        id=item_id,
        name="Speed Booster",
        description="Boosts speed",
        type=ItemType.ARTIFACT,
        rarity="uncommon",
        effect=effect or {"bonus_speed": 0.15, "slot_type": "speed"},
    )


@pytest.fixture
def mock_item_repo():
    repo = MagicMock()
    repo.get_by_id = AsyncMock()
    return repo


@pytest.fixture
def mock_inventory_repo():
    repo = MagicMock()
    repo.get_by_player_id = AsyncMock()
    repo.save = AsyncMock()
    return repo


@pytest.fixture
def mock_equipment_repo():
    repo = MagicMock()
    repo.get_by_ship_id = AsyncMock()
    repo.save = AsyncMock()
    return repo


class TestEquipArtifactUseCase:
    @pytest.mark.asyncio
    async def test_equip_artifact_success(self, mock_item_repo, mock_inventory_repo, mock_equipment_repo, mock_uow):
        player_id = uuid4()
        ship_id = uuid4()
        item_id = uuid4()

        player = make_player(player_id, ships=[make_ship(ship_id, player_id)])
        artifact = make_artifact(item_id, effect={"bonus_speed": 0.15, "slot_type": "speed"})
        dto = EquipArtifactDTO(ship_id=ship_id, item_id=item_id)

        mock_item_repo.get_by_id.return_value = artifact

        inventory = MagicMock()
        inventory.has_item.return_value = True
        mock_inventory_repo.get_by_player_id.return_value = inventory

        mock_equipment_repo.get_by_ship_id.return_value = None

        use_case = EquipArtifactUseCase(mock_item_repo, mock_inventory_repo, mock_equipment_repo)

        result = await use_case.execute(player, dto, mock_uow)

        assert "Equipped" in result.message
        assert len(result.equipment.artifacts) == 1
        assert result.equipment.artifacts[0].slot_type == "speed"

        mock_equipment_repo.save.assert_awaited_once()
        mock_inventory_repo.save.assert_awaited_once()
        mock_uow.track.assert_called_once()
        mock_uow.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_equip_ship_not_found(self, mock_item_repo, mock_inventory_repo, mock_equipment_repo, mock_uow):
        player_id = uuid4()
        player = make_player(player_id, ships=[])
        dto = EquipArtifactDTO(ship_id=uuid4(), item_id=uuid4())

        use_case = EquipArtifactUseCase(mock_item_repo, mock_inventory_repo, mock_equipment_repo)

        with pytest.raises(ShipNotFoundError):
            await use_case.execute(player, dto, mock_uow)

    @pytest.mark.asyncio
    async def test_equip_item_not_found(self, mock_item_repo, mock_inventory_repo, mock_equipment_repo, mock_uow):
        player_id = uuid4()
        ship_id = uuid4()
        player = make_player(player_id, ships=[make_ship(ship_id, player_id)])
        dto = EquipArtifactDTO(ship_id=ship_id, item_id=uuid4())

        mock_item_repo.get_by_id.return_value = None

        use_case = EquipArtifactUseCase(mock_item_repo, mock_inventory_repo, mock_equipment_repo)

        with pytest.raises(ItemNotFoundError):
            await use_case.execute(player, dto, mock_uow)

    @pytest.mark.asyncio
    async def test_equip_not_in_inventory(self, mock_item_repo, mock_inventory_repo, mock_equipment_repo, mock_uow):
        player_id = uuid4()
        ship_id = uuid4()
        item_id = uuid4()
        player = make_player(player_id, ships=[make_ship(ship_id, player_id)])
        artifact = make_artifact(item_id)
        dto = EquipArtifactDTO(ship_id=ship_id, item_id=item_id)

        mock_item_repo.get_by_id.return_value = artifact

        inventory = MagicMock()
        inventory.has_item.return_value = False
        mock_inventory_repo.get_by_player_id.return_value = inventory

        use_case = EquipArtifactUseCase(mock_item_repo, mock_inventory_repo, mock_equipment_repo)

        with pytest.raises(ItemNotInInventoryError):
            await use_case.execute(player, dto, mock_uow)

    @pytest.mark.asyncio
    async def test_equip_non_artifact_raises_error(self, mock_item_repo, mock_inventory_repo, mock_equipment_repo, mock_uow):
        player_id = uuid4()
        ship_id = uuid4()
        item_id = uuid4()
        player = make_player(player_id, ships=[make_ship(ship_id, player_id)])
        consumable = Item(
            id=item_id,
            name="Tea",
            description="Restores tea",
            type=ItemType.CONSUMABLE,
            effect={"restore_tea": 50},
        )
        dto = EquipArtifactDTO(ship_id=ship_id, item_id=item_id)

        mock_item_repo.get_by_id.return_value = consumable

        inventory = MagicMock()
        inventory.has_item.return_value = True
        mock_inventory_repo.get_by_player_id.return_value = inventory

        use_case = EquipArtifactUseCase(mock_item_repo, mock_inventory_repo, mock_equipment_repo)

        with pytest.raises(ValueError, match="not an artifact"):
            await use_case.execute(player, dto, mock_uow)

    @pytest.mark.asyncio
    async def test_equip_replaces_artifact_returns_to_inventory(
        self, mock_item_repo, mock_inventory_repo, mock_equipment_repo, mock_uow
    ):
        player_id = uuid4()
        ship_id = uuid4()
        item_id_a = uuid4()
        item_id_b = uuid4()

        player = make_player(player_id, ships=[make_ship(ship_id, player_id)])

        artifact_b = make_artifact(item_id_b, effect={"bonus_speed": 0.2, "slot_type": "speed"})

        mock_item_repo.get_by_id.return_value = artifact_b

        inventory = MagicMock()
        inventory.has_item.return_value = True
        inventory.add_item = MagicMock()
        inventory.remove_item = MagicMock()
        mock_inventory_repo.get_by_player_id.return_value = inventory

        existing_equipment = Equipment(ship_id=ship_id)
        existing_equipment.equip(item_id_a, SlotType.SPEED, {"speed": 0.1})
        mock_equipment_repo.get_by_ship_id.return_value = existing_equipment

        use_case = EquipArtifactUseCase(mock_item_repo, mock_inventory_repo, mock_equipment_repo)

        result = await use_case.execute(
            player, EquipArtifactDTO(ship_id=ship_id, item_id=item_id_b), mock_uow
        )

        assert "Equipped" in result.message
        assert len(result.equipment.artifacts) == 1
        assert result.equipment.artifacts[0].item_id == item_id_b

        inventory.add_item.assert_called_once_with(item_id_a, quantity=1)
        inventory.remove_item.assert_called_once_with(item_id_b, quantity=1)
        mock_equipment_repo.save.assert_awaited_once()
        mock_inventory_repo.save.assert_awaited_once()
        mock_uow.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_equip_multiple_artifacts_stacks_bonuses(self, mock_uow):
        player_id = uuid4()
        ship_id = uuid4()
        item_id_1 = uuid4()
        item_id_2 = uuid4()
        player = make_player(player_id, ships=[make_ship(ship_id, player_id)])
        dto_1 = EquipArtifactDTO(ship_id=ship_id, item_id=item_id_1)
        dto_2 = EquipArtifactDTO(ship_id=ship_id, item_id=item_id_2)

        artifact_1 = make_artifact(item_id_1, effect={"bonus_speed": 0.1, "slot_type": "speed"})
        artifact_2 = make_artifact(item_id_2, effect={"bonus_luck": 0.05, "slot_type": "luck"})

        item_repo = MagicMock()
        item_repo.get_by_id = AsyncMock()
        item_repo.get_by_id.side_effect = [artifact_1, artifact_2]

        inventory = MagicMock()
        inventory.has_item.return_value = True
        inventory_repo = MagicMock()
        inventory_repo.get_by_player_id = AsyncMock(return_value=inventory)
        inventory_repo.save = AsyncMock()

        stored_equipment: Equipment | None = None

        equipment_repo = MagicMock(spec=EquipmentRepository)
        async def fake_get(ship_id):
            return stored_equipment
        async def fake_save(equip):
            nonlocal stored_equipment
            stored_equipment = equip
        equipment_repo.get_by_ship_id = fake_get
        equipment_repo.save = fake_save

        use_case = EquipArtifactUseCase(item_repo, inventory_repo, equipment_repo)

        result_1 = await use_case.execute(player, dto_1, mock_uow)
        assert len(result_1.equipment.artifacts) == 1
        assert result_1.equipment.artifacts[0].slot_type == "speed"

        result_2 = await use_case.execute(player, dto_2, mock_uow)
        assert len(result_2.equipment.artifacts) == 2

        assert stored_equipment is not None
        bonuses = stored_equipment.get_total_bonuses()
        assert bonuses["speed"] == 0.1
        assert bonuses["luck"] == 0.05


class TestUnequipArtifactUseCase:
    @pytest.mark.asyncio
    async def test_unequip_artifact_success(self, mock_inventory_repo, mock_equipment_repo, mock_uow):
        player_id = uuid4()
        ship_id = uuid4()
        item_id = uuid4()
        player = make_player(player_id, ships=[make_ship(ship_id, player_id)])
        dto = UnequipArtifactDTO(ship_id=ship_id, item_id=item_id)

        equipment = Equipment(ship_id=ship_id)
        equipment.equip(item_id, SlotType.SPEED, {"speed": 0.1})
        mock_equipment_repo.get_by_ship_id.return_value = equipment

        inventory = MagicMock()
        inventory.add_item = MagicMock()
        mock_inventory_repo.get_by_player_id.return_value = inventory

        use_case = UnequipArtifactUseCase(mock_inventory_repo, mock_equipment_repo)

        result = await use_case.execute(player, dto, mock_uow)

        assert "Unequipped" in result.message
        assert len(result.equipment.artifacts) == 0

        inventory.add_item.assert_called_once_with(item_id, quantity=1)
        mock_equipment_repo.save.assert_awaited_once()
        mock_inventory_repo.save.assert_awaited_once()
        mock_uow.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_unequip_ship_not_found(self, mock_inventory_repo, mock_equipment_repo, mock_uow):
        player_id = uuid4()
        player = make_player(player_id, ships=[])
        dto = UnequipArtifactDTO(ship_id=uuid4(), item_id=uuid4())

        use_case = UnequipArtifactUseCase(mock_inventory_repo, mock_equipment_repo)

        with pytest.raises(ShipNotFoundError):
            await use_case.execute(player, dto, mock_uow)

    @pytest.mark.asyncio
    async def test_unequip_no_equipment(self, mock_inventory_repo, mock_equipment_repo, mock_uow):
        player_id = uuid4()
        ship_id = uuid4()
        player = make_player(player_id, ships=[make_ship(ship_id, player_id)])
        dto = UnequipArtifactDTO(ship_id=ship_id, item_id=uuid4())

        mock_equipment_repo.get_by_ship_id.return_value = None

        use_case = UnequipArtifactUseCase(mock_inventory_repo, mock_equipment_repo)

        with pytest.raises(Exception):
            await use_case.execute(player, dto, mock_uow)
