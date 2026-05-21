"""Integration-тесты для API эндпоинтов."""

from __future__ import annotations

import json

import pytest
import pytest_asyncio
from httpx import AsyncClient

from tests.conftest import mock_telegram_user


@pytest.mark.asyncio
async def test_health_endpoint(async_client: AsyncClient):
    """GET /health должен возвращать 200 со статусом БД и Redis."""
    response = await async_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "ok" in data
    assert "database" in data
    assert "redis" in data
    assert "env" in data


@pytest.mark.asyncio
async def test_root_endpoint(async_client: AsyncClient):
    """GET / должен возвращать 200."""
    response = await async_client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "running"
    assert data["service"] == "exo-genesis-api"


@pytest.mark.asyncio
async def test_config_fuels_endpoint(async_client: AsyncClient):
    """GET /config/fuels должен возвращать 200 с валидным JSON."""
    response = await async_client.get("/config/fuels")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert len(data) > 0
    # Проверяем структуру первого элемента
    first_key = next(iter(data))
    first_item = data[first_key]
    assert "name" in first_item
    assert "tier" in first_item
    assert "slug" in first_item


@pytest.mark.asyncio
async def test_config_ships_endpoint(async_client: AsyncClient):
    """GET /config/ships должен возвращать 200 с валидным JSON."""
    response = await async_client.get("/config/ships")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "seeker_dust_runner" in data


@pytest.mark.asyncio
async def test_config_cache_headers(async_client: AsyncClient):
    """GET /config/* должен возвращать заголовок X-Cache: HIT/MISS."""
    # Первый запрос — MISS
    response1 = await async_client.get("/config/fuels")
    assert response1.status_code == 200
    cache_header1 = response1.headers.get("X-Cache")
    assert cache_header1 in ("HIT", "MISS")

    # Второй запрос — должен быть HIT (из кэша)
    response2 = await async_client.get("/config/fuels")
    assert response2.status_code == 200
    cache_header2 = response2.headers.get("X-Cache")
    assert cache_header2 == "HIT"


@pytest.mark.asyncio
async def test_expeditions_start_requires_auth(async_client: AsyncClient):
    """POST /expeditions/start без авторизации должен возвращать 401."""
    response = await async_client.post(
        "/expeditions/start",
        json={
            "ship_slug": "seeker_dust_runner",
            "tier": 1,
            "fuel_slug": "fuel_t1_mangan_hydride",
            "overdrive_mode": "stable",
        },
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_expeditions_start_with_auth(async_client: AsyncClient):
    """POST /expeditions/start с авторизацией должен обрабатывать запрос."""
    headers = {"X-Telegram-User": mock_telegram_user()}
    response = await async_client.post(
        "/expeditions/start",
        json={
            "ship_slug": "seeker_dust_runner",
            "tier": 1,
            "fuel_slug": "fuel_t1_mangan_hydride",
            "overdrive_mode": "stable",
        },
        headers=headers,
    )
    # Может быть 200 (успех) или 400 (нехватка топлива/корабля)
    assert response.status_code in (200, 400, 422)


@pytest.mark.asyncio
async def test_laboratory_craft_requires_auth(async_client: AsyncClient):
    """POST /laboratory/craft без авторизации должен возвращать 401."""
    response = await async_client.post(
        "/laboratory/craft",
        json={
            "domain_slug": "zone_inner_rim",
            "essences": ["essence_t1", "essence_t2", "essence_t3"],
            "xgen_amount": 100,
        },
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_laboratory_craft_with_invalid_essences(async_client: AsyncClient):
    """POST /laboratory/craft с недостатком эссенций должен возвращать 400."""
    headers = {"X-Telegram-User": mock_telegram_user()}
    response = await async_client.post(
        "/laboratory/craft",
        json={
            "domain_slug": "zone_inner_rim",
            "essences": ["essence_t1"],  # Минимум 3
            "xgen_amount": 100,
        },
        headers=headers,
    )
    assert response.status_code in (400, 422)


@pytest.mark.asyncio
async def test_config_invalid_name(async_client: AsyncClient):
    """GET /config/ с небезопасным именем должен возвращать 404."""
    response = await async_client.get("/config/../../../etc/passwd")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_config_nonexistent(async_client: AsyncClient):
    """GET /config/nonexistent должен возвращать 404."""
    response = await async_client.get("/config/nonexistent_config")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_auth_me_endpoint(async_client: AsyncClient):
    """GET /auth/me с авторизацией должен возвращать профиль."""
    headers = {"X-Telegram-User": mock_telegram_user()}
    response = await async_client.get("/auth/me", headers=headers)
    # Может быть 200 или 404 (если игрок не создан)
    assert response.status_code in (200, 404)
