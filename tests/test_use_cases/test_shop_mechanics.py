from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.application.dtos.admin_dto import CreateShopItemDTO, UpdateShopItemDTO


class TestCreateShopItemValidation:
    """Tests for CreateShopItemDTO stock_limit validation."""

    def test_create_shop_item_negative_stock_limit(self):
        with pytest.raises(ValidationError):
            CreateShopItemDTO(
                item_id=uuid4(),
                price_xgen=100,
                daily_limit=0,
                stock_limit=-1,
                is_active=True,
            )

    def test_create_shop_item_negative_daily_limit(self):
        with pytest.raises(ValidationError):
            CreateShopItemDTO(
                item_id=uuid4(),
                price_xgen=100,
                daily_limit=-5,
                stock_limit=0,
                is_active=True,
            )

    def test_create_shop_item_negative_price_xgen(self):
        with pytest.raises(ValidationError):
            CreateShopItemDTO(
                item_id=uuid4(),
                price_xgen=-10,
                daily_limit=0,
                stock_limit=0,
                is_active=True,
            )

    def test_create_shop_item_valid(self):
        item = CreateShopItemDTO(
            item_id=uuid4(),
            price_xgen=100,
            daily_limit=5,
            stock_limit=50,
            is_active=True,
        )
        assert item.price_xgen == 100
        assert item.daily_limit == 5
        assert item.stock_limit == 50


class TestUpdateShopItemValidation:
    """Tests for UpdateShopItemDTO stock_limit validation."""

    def test_update_shop_item_negative_stock_limit(self):
        with pytest.raises(ValueError, match="stock_limit must be >= 0"):
            UpdateShopItemDTO(stock_limit=-1)

    def test_update_shop_item_negative_daily_limit(self):
        with pytest.raises(ValueError, match="daily_limit must be >= 0"):
            UpdateShopItemDTO(daily_limit=-1)

    def test_update_shop_item_negative_price_xgen(self):
        with pytest.raises(ValueError, match="price_xgen must be >= 0"):
            UpdateShopItemDTO(price_xgen=-1)

    def test_update_shop_item_valid(self):
        item = UpdateShopItemDTO(
            price_xgen=50,
            daily_limit=10,
            stock_limit=100,
        )
        assert item.price_xgen == 50
        assert item.daily_limit == 10
        assert item.stock_limit == 100

    def test_update_shop_item_partial_update(self):
        item = UpdateShopItemDTO(price_xgen=200)
        assert item.price_xgen == 200
        assert item.daily_limit is None
        assert item.stock_limit is None
