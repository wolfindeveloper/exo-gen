GET    /admin/items           - Список предметов (пагинация, поиск)
POST   /admin/items           - Создать предмет
PATCH  /admin/items/{id}      - Обновить предмет
DELETE /admin/items/{id}      - Мягкое удаление

GET    /admin/zones           - Список зон
POST   /admin/zones           - Создать зону
PATCH  /admin/zones/{id}      - Обновить зону
POST   /admin/zones/{id}/simulate-loot  - Симуляция 100 экспедиций

GET    /admin/loot-boxes      - Список лутбоксов
POST   /admin/loot-boxes      - Создать лутбокс
POST   /admin/loot-boxes/{id}/simulate    - Симуляция 1000 открытий

GET    /admin/chapters        - Список глав
PATCH  /admin/chapters/{id}/reorder-articles - Drag-and-Drop сортировка

GET    /admin/shop-items      - Список товаров магазина
GET    /admin/shop-items/{id}/analytics    - Аналитика покупок
POST   /admin/shop-items      - Создать товар (в т.ч. бандлы)