from unittest.mock import MagicMock, AsyncMock
from uuid import uuid4

import pytest

from app.application.use_cases.refuel_ship import RefuelShipUseCase
from app.application.use_cases.repair_ship import RepairShipUseCase
from app.application.dtos.ship_service_dto import RefuelShipDTO, RepairShipDTO
from app.domain.entities.player import Player
from app.domain.entities.ship import Ship
from app.domain.entities.item import Item, ItemType
from app.domain.value_objects.resources import TeaLevel, Optimism, XgenBalance, FragmentsBalance
from app.domain.exceptions.ship import ShipNotFoundError
from app.domain.exceptions.inventory import NoSuitableConsumableError


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


def make_consumable(item_id, effect_key, effect_value):
    return Item(
        id=item_id,
        name="Tea Canister" if effect_key == "restore_tea" else "Repair Kit",
        description="Restores resource",
        type=ItemType.CONSUMABLE,
        effect={effect_key: effect_value},
    )


@pytest.fixture
def mock_item_repo():
    repo = MagicMock()
    repo.get_consumables_with_effect = AsyncMock()
    return repo


class TestRefuelShipUseCase:
    @pytest.mark.asyncio
    async def test_refuel_success(
        self, mock_player_repo, mock_inventory_repo, mock_item_repo, mock_uow, player_id
    ):
        ship_id = uuid4()
        fuel_item_id = uuid4()

        player = make_player(player_id, ships=[make_ship(ship_id, player_id)])
        player.ships[0].tea_level = TeaLevel(30.0)

        fuel_item = make_consumable(fuel_item_id, "restore_tea", 50.0)
        mock_item_repo.get_consumables_with_effect.return_value = [fuel_item]

        inventory = MagicMock()
        inventory.has_item.return_value = True
        inventory.remove_item = MagicMock()
        mock_inventory_repo.get_by_player_id.return_value = inventory

        use_case = RefuelShipUseCase(mock_player_repo, mock_inventory_repo, mock_item_repo)
        result = await use_case.execute(player, RefuelShipDTO(ship_id=ship_id), mock_uow)

        assert result.new_tea_level == 80.0
        assert result.item_used_id == fuel_item_id
        assert result.tea_restored == 50.0
        inventory.remove_item.assert_called_once_with(fuel_item_id, quantity=1)
        mock_player_repo.save.assert_awaited_once()
        mock_inventory_repo.save.assert_awaited_once()
        mock_uow.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_refuel_no_consumable_in_world(
        self, mock_player_repo, mock_inventory_repo, mock_item_repo, mock_uow, player_id
    ):
        ship_id = uuid4()
        player = make_player(player_id, ships=[make_ship(ship_id, player_id)])

        mock_item_repo.get_consumables_with_effect.return_value = []

        use_case = RefuelShipUseCase(mock_player_repo, mock_inventory_repo, mock_item_repo)

        with pytest.raises(NoSuitableConsumableError, match="restore_tea"):
            await use_case.execute(player, RefuelShipDTO(ship_id=ship_id), mock_uow)

        mock_player_repo.save.assert_not_called()
        mock_inventory_repo.save.assert_not_called()
        mock_uow.commit.assert_not_called()

    @pytest.mark.asyncio
    async def test_refuel_consumable_exists_but_not_in_inventory(
        self, mock_player_repo, mock_inventory_repo, mock_item_repo, mock_uow, player_id
    ):
        ship_id = uuid4()
        fuel_item_id = uuid4()
        player = make_player(player_id, ships=[make_ship(ship_id, player_id)])

        fuel_item = make_consumable(fuel_item_id, "restore_tea", 50.0)
        mock_item_repo.get_consumables_with_effect.return_value = [fuel_item]

        inventory = MagicMock()
        inventory.has_item.return_value = False
        mock_inventory_repo.get_by_player_id.return_value = inventory

        use_case = RefuelShipUseCase(mock_player_repo, mock_inventory_repo, mock_item_repo)

        with pytest.raises(NoSuitableConsumableError, match="restore_tea"):
            await use_case.execute(player, RefuelShipDTO(ship_id=ship_id), mock_uow)

        mock_player_repo.save.assert_not_called()
        mock_inventory_repo.save.assert_not_called()
        mock_uow.commit.assert_not_called()

    @pytest.mark.asyncio
    async def test_refuel_ship_not_found(
        self, mock_player_repo, mock_inventory_repo, mock_item_repo, mock_uow, player_id
    ):
        player = make_player(player_id, ships=[])

        use_case = RefuelShipUseCase(mock_player_repo, mock_inventory_repo, mock_item_repo)

        with pytest.raises(ShipNotFoundError):
            await use_case.execute(player, RefuelShipDTO(ship_id=uuid4()), mock_uow)

        mock_player_repo.save.assert_not_called()
        mock_inventory_repo.save.assert_not_called()
        mock_uow.commit.assert_not_called()


class TestRepairShipUseCase:
    @pytest.mark.asyncio
    async def test_repair_success(
        self, mock_player_repo, mock_inventory_repo, mock_item_repo, mock_uow, player_id
    ):
        ship_id = uuid4()
        repair_item_id = uuid4()

        player = make_player(player_id, ships=[make_ship(ship_id, player_id)])
        player.ships[0].optimism = Optimism(50.0)

        repair_item = make_consumable(repair_item_id, "restore_optimism", 30.0)
        mock_item_repo.get_consumables_with_effect.return_value = [repair_item]

        inventory = MagicMock()
        inventory.has_item.return_value = True
        inventory.remove_item = MagicMock()
        mock_inventory_repo.get_by_player_id.return_value = inventory

        use_case = RepairShipUseCase(mock_player_repo, mock_inventory_repo, mock_item_repo)
        result = await use_case.execute(player, RepairShipDTO(ship_id=ship_id), mock_uow)

        assert result.new_optimism_level == 80.0
        assert result.item_used_id == repair_item_id
        assert result.optimism_restored == 30.0
        inventory.remove_item.assert_called_once_with(repair_item_id, quantity=1)
        mock_player_repo.save.assert_awaited_once()
        mock_inventory_repo.save.assert_awaited_once()
        mock_uow.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_repair_no_consumable(
        self, mock_player_repo, mock_inventory_repo, mock_item_repo, mock_uow, player_id
    ):
        ship_id = uuid4()
        player = make_player(player_id, ships=[make_ship(ship_id, player_id)])

        mock_item_repo.get_consumables_with_effect.return_value = []

        use_case = RepairShipUseCase(mock_player_repo, mock_inventory_repo, mock_item_repo)

        with pytest.raises(NoSuitableConsumableError, match="restore_optimism"):
            await use_case.execute(player, RepairShipDTO(ship_id=ship_id), mock_uow)

        mock_player_repo.save.assert_not_called()
        mock_inventory_repo.save.assert_not_called()
        mock_uow.commit.assert_not_called()
