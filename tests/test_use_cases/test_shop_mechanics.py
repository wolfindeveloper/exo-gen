from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.application.dtos.admin_dto import CreateShopItemDTO, UpdateShopItemDTO
from app.application.dtos.shop_dto import CreateShopCategoryDTO, UpdateShopCategoryDTO
from app.application.use_cases.create_shop_category import CreateShopCategoryUseCase
from app.application.use_cases.get_shop_categories import GetShopCategoriesUseCase
from app.application.use_cases.soft_delete_shop_category import SoftDeleteShopCategoryUseCase
from app.application.use_cases.update_shop_category import UpdateShopCategoryUseCase
from app.application.use_cases.update_shop_item import UpdateShopItemUseCase
from app.domain.entities.shop import ShopCategory, ShopItem
from app.domain.exceptions.shop import (
    ShopCategoryHasItemsError,
    ShopCategoryNotFoundError,
    ShopCategorySlugTakenError,
    ShopItemNotFoundError,
)


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


class TestShopCategoryDto:
    def test_create_shop_category_dto_defaults(self):
        dto = CreateShopCategoryDTO(name="Ресурсы", slug="resources")
        assert dto.icon == ""
        assert dto.sort_order == 0

    def test_update_shop_category_dto_none_defaults(self):
        dto = UpdateShopCategoryDTO()
        assert dto.name is None
        assert dto.icon is None
        assert dto.sort_order is None
        assert dto.is_active is None


class TestCreateShopCategory:
    @pytest.mark.asyncio
    async def test_create_category_success(self, monkeypatch):
        created = {}

        class FakeRepo:
            def __init__(self):
                self.saved = []

            async def get_by_slug(self, slug):
                return None

            async def save(self, category):
                self.saved.append(category)

            async def commit(self):
                pass

        class FakeUow:
            def track(self, entity):
                pass

            async def commit(self):
                pass

        repo = FakeRepo()
        uow = FakeUow()
        use_case = CreateShopCategoryUseCase(repo)

        category = await use_case.execute(
            CreateShopCategoryDTO(name="Ресурсы", slug="resources", icon="package", sort_order=1),
            uow,
        )

        assert category.name == "Ресурсы"
        assert category.slug == "resources"
        assert category.icon == "package"
        assert category.sort_order == 1
        assert category.is_active is True
        assert repo.saved == [category]

    @pytest.mark.asyncio
    async def test_create_category_duplicate_slug_raises(self):
        existing = ShopCategory(id=uuid4(), name="Ресурсы", slug="resources")

        class FakeRepo:
            async def get_by_slug(self, slug):
                return existing

            async def save(self, category):
                pass

        class FakeUow:
            async def commit(self):
                pass

        use_case = CreateShopCategoryUseCase(FakeRepo())

        with pytest.raises(ShopCategorySlugTakenError):
            await use_case.execute(CreateShopCategoryDTO(name="Другое", slug="resources"), FakeUow())


class TestUpdateShopCategory:
    @pytest.mark.asyncio
    async def test_update_category_success(self):
        category = ShopCategory(id=uuid4(), name="Ресурсы", slug="resources")

        class FakeRepo:
            async def get_by_id(self, category_id):
                return category

            async def save(self, entity):
                pass

        class FakeUow:
            def track(self, entity):
                pass

            async def commit(self):
                pass

        use_case = UpdateShopCategoryUseCase(FakeRepo())
        updated = await use_case.execute(
            category.id,
            UpdateShopCategoryDTO(name="Ресурсы V2", icon="diamond", sort_order=5, is_active=False),
            FakeUow(),
        )

        assert updated.name == "Ресурсы V2"
        assert updated.icon == "diamond"
        assert updated.sort_order == 5
        assert updated.is_active is False

    @pytest.mark.asyncio
    async def test_update_missing_category_raises(self):
        class FakeRepo:
            async def get_by_id(self, category_id):
                return None

            async def save(self, entity):
                pass

        class FakeUow:
            async def commit(self):
                pass

        use_case = UpdateShopCategoryUseCase(FakeRepo())
        with pytest.raises(ShopCategoryNotFoundError):
            await use_case.execute(uuid4(), UpdateShopCategoryDTO(name="X"), FakeUow())


class TestSoftDeleteShopCategory:
    @pytest.mark.asyncio
    async def test_delete_missing_category_raises(self):
        class FakeRepo:
            async def get_by_id(self, category_id):
                return None

            async def count_items_by_category(self, category_id):
                return 0

            async def save(self, entity):
                pass

        class FakeUow:
            async def commit(self):
                pass

        use_case = SoftDeleteShopCategoryUseCase(FakeRepo())
        with pytest.raises(ShopCategoryNotFoundError):
            await use_case.execute(uuid4(), FakeUow())

    @pytest.mark.asyncio
    async def test_delete_category_with_items_raises(self):
        category = ShopCategory(id=uuid4(), name="Ресурсы", slug="resources")

        class FakeRepo:
            async def get_by_id(self, category_id):
                return category

            async def count_items_by_category(self, category_id):
                return 3

            async def save(self, entity):
                pass

        class FakeUow:
            async def commit(self):
                pass

        use_case = SoftDeleteShopCategoryUseCase(FakeRepo())
        with pytest.raises(ShopCategoryHasItemsError):
            await use_case.execute(category.id, FakeUow())

    @pytest.mark.asyncio
    async def test_delete_category_success(self):
        category = ShopCategory(id=uuid4(), name="Ресурсы", slug="resources")

        class FakeRepo:
            def __init__(self):
                self.saved = []

            async def get_by_id(self, category_id):
                return category

            async def count_items_by_category(self, category_id):
                return 0

            async def save(self, entity):
                self.saved.append(entity)

        class FakeUow:
            def track(self, entity):
                pass

            async def commit(self):
                pass

        use_case = SoftDeleteShopCategoryUseCase(FakeRepo())
        uow = FakeUow()
        await use_case.execute(category.id, uow)

        assert category.is_deleted()
        assert use_case.category_repo.saved == [category]


class TestGetShopCategories:
    @pytest.mark.asyncio
    async def test_maps_categories_to_dtos(self):
        active = ShopCategory(id=uuid4(), name="Ресурсы", slug="resources", sort_order=1)
        inactive = ShopCategory(id=uuid4(), name="Скрытая", slug="hidden", is_active=False)

        class FakeRepo:
            async def get_all_active(self):
                return [active, inactive]

        use_case = GetShopCategoriesUseCase(FakeRepo())
        result = await use_case.execute()

        assert len(result) == 2
        assert result[0].slug == "resources"
        assert result[0].name == "Ресурсы"
        assert result[0].sort_order == 1
        assert result[1].is_active is False


class TestUpdateShopItemCategory:
    @pytest.mark.asyncio
    async def test_update_item_assign_category(self):
        item = ShopItem(id=uuid4(), price_xgen=100)
        category_id = uuid4()

        class FakeRepo:
            async def get_by_id(self, item_id):
                return item

            async def save(self, entity):
                pass

        class FakeUow:
            def track(self, entity):
                pass

            async def commit(self):
                pass

        use_case = UpdateShopItemUseCase(FakeRepo())
        updated = await use_case.execute(item.id, UpdateShopItemDTO(category_id=category_id), FakeUow())

        assert updated.category_id == category_id

    @pytest.mark.asyncio
    async def test_update_item_clear_category(self):
        item = ShopItem(id=uuid4(), price_xgen=100, category_id=uuid4())

        class FakeRepo:
            async def get_by_id(self, item_id):
                return item

            async def save(self, entity):
                pass

        class FakeUow:
            def track(self, entity):
                pass

            async def commit(self):
                pass

        use_case = UpdateShopItemUseCase(FakeRepo())
        updated = await use_case.execute(item.id, UpdateShopItemDTO(category_id=None), FakeUow())

        assert updated.category_id is None

    @pytest.mark.asyncio
    async def test_update_missing_item_raises(self):
        class FakeRepo:
            async def get_by_id(self, item_id):
                return None

            async def save(self, entity):
                pass

        class FakeUow:
            async def commit(self):
                pass

        use_case = UpdateShopItemUseCase(FakeRepo())
        with pytest.raises(ShopItemNotFoundError):
            await use_case.execute(uuid4(), UpdateShopItemDTO(price_xgen=10), FakeUow())
