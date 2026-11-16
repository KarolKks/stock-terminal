import pytest
from httpx import AsyncClient

from app.services.market_data import market_data_service


pytestmark = pytest.mark.asyncio


async def test_create_list_and_reject_duplicate_category(
    ac: AsyncClient,
    auth_headers: dict[str, str],
):
    create_response = await ac.post(
        "/watchlists/categories",
        json={"name": "  Tech  "},
        headers=auth_headers,
    )

    assert create_response.status_code == 201
    assert create_response.json()["name"] == "Tech"
    assert create_response.json()["items"] == []

    duplicate_response = await ac.post(
        "/watchlists/categories",
        json={"name": "tech"},
        headers=auth_headers,
    )
    assert duplicate_response.status_code == 400

    list_response = await ac.get("/watchlists/categories", headers=auth_headers)
    assert list_response.status_code == 200
    assert [category["name"] for category in list_response.json()] == ["Tech"]


async def test_add_ticker_normalizes_symbol_and_rejects_duplicate(
    ac: AsyncClient,
    auth_headers: dict[str, str],
    monkeypatch: pytest.MonkeyPatch,
):
    ticker_checks: list[str] = []

    async def ticker_exists(ticker: str) -> bool:
        ticker_checks.append(ticker)
        return True

    monkeypatch.setattr(market_data_service, "ticker_exists", ticker_exists)

    category_response = await ac.post(
        "/watchlists/categories",
        json={"name": "Tech"},
        headers=auth_headers,
    )
    category_id = category_response.json()["id"]

    item_response = await ac.post(
        f"/watchlists/categories/{category_id}/items",
        json={"ticker": " aapl "},
        headers=auth_headers,
    )
    assert item_response.status_code == 201
    assert item_response.json()["ticker"] == "AAPL"
    assert ticker_checks == ["AAPL"]

    duplicate_response = await ac.post(
        f"/watchlists/categories/{category_id}/items",
        json={"ticker": "AAPL"},
        headers=auth_headers,
    )
    assert duplicate_response.status_code == 400
    assert ticker_checks == ["AAPL"]


async def test_add_ticker_rejects_unknown_market_symbol(
    ac: AsyncClient,
    auth_headers: dict[str, str],
    monkeypatch: pytest.MonkeyPatch,
):
    async def ticker_does_not_exist(_ticker: str) -> bool:
        return False

    monkeypatch.setattr(
        market_data_service, "ticker_exists", ticker_does_not_exist
    )

    category_response = await ac.post(
        "/watchlists/categories",
        json={"name": "Tech"},
        headers=auth_headers,
    )
    category_id = category_response.json()["id"]

    response = await ac.post(
        f"/watchlists/categories/{category_id}/items",
        json={"ticker": "NOTAREALTICKER"},
        headers=auth_headers,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == (
        "Ticker 'NOTAREALTICKER' was not found on market exchanges."
    )


async def test_rename_category_preserves_items_and_rejects_duplicate(
    ac: AsyncClient,
    auth_headers: dict[str, str],
    monkeypatch: pytest.MonkeyPatch,
):
    async def ticker_exists(_ticker: str) -> bool:
        return True

    monkeypatch.setattr(market_data_service, "ticker_exists", ticker_exists)

    tech_response = await ac.post(
        "/watchlists/categories",
        json={"name": "Tech"},
        headers=auth_headers,
    )
    growth_response = await ac.post(
        "/watchlists/categories",
        json={"name": "Growth"},
        headers=auth_headers,
    )
    tech_id = tech_response.json()["id"]

    await ac.post(
        f"/watchlists/categories/{tech_id}/items",
        json={"ticker": "AAPL"},
        headers=auth_headers,
    )

    rename_response = await ac.patch(
        f"/watchlists/categories/{tech_id}",
        json={"name": "Long-term picks"},
        headers=auth_headers,
    )
    assert rename_response.status_code == 200
    assert rename_response.json()["name"] == "Long-term picks"
    assert [item["ticker"] for item in rename_response.json()["items"]] == ["AAPL"]

    duplicate_response = await ac.patch(
        f"/watchlists/categories/{tech_id}",
        json={"name": " growth "},
        headers=auth_headers,
    )
    assert duplicate_response.status_code == 400
    assert growth_response.status_code == 201


async def test_watchlist_routes_require_authentication(ac: AsyncClient):
    response = await ac.get("/watchlists/categories")
    assert response.status_code in (401, 403)


async def test_remove_ticker(
    ac: AsyncClient,
    auth_headers: dict[str, str],
    monkeypatch: pytest.MonkeyPatch,
):
    async def ticker_exists(_ticker: str) -> bool:
        return True

    monkeypatch.setattr(market_data_service, "ticker_exists", ticker_exists)

    category_response = await ac.post(
        "/watchlists/categories",
        json={"name": "Tech"},
        headers=auth_headers,
    )
    category_id = category_response.json()["id"]

    add_response = await ac.post(
        f"/watchlists/categories/{category_id}/items",
        json={"ticker": "AAPL"},
        headers=auth_headers,
    )
    assert add_response.status_code == 201

    remove_response = await ac.delete(
        f"/watchlists/categories/{category_id}/items/aapl",
        headers=auth_headers,
    )
    assert remove_response.status_code == 204


async def test_delete_category_with_items(
    ac: AsyncClient,
    auth_headers: dict[str, str],
    monkeypatch: pytest.MonkeyPatch,
):
    async def ticker_exists(_ticker: str) -> bool:
        return True

    monkeypatch.setattr(market_data_service, "ticker_exists", ticker_exists)

    category_response = await ac.post(
        "/watchlists/categories",
        json={"name": "Tech"},
        headers=auth_headers,
    )
    category_id = category_response.json()["id"]

    add_response = await ac.post(
        f"/watchlists/categories/{category_id}/items",
        json={"ticker": "AAPL"},
        headers=auth_headers,
    )
    assert add_response.status_code == 201

    delete_response = await ac.delete(
        f"/watchlists/categories/{category_id}",
        headers=auth_headers,
    )
    assert delete_response.status_code == 204

    list_response = await ac.get("/watchlists/categories", headers=auth_headers)
    assert list_response.status_code == 200
    assert list_response.json() == []
