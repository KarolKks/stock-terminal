import pytest
from httpx import AsyncClient

from app.schemas.market import CandlePoint, CandleSeriesResponse
from app.services.market_data import (
    MarketDataNotFoundError,
    MarketDataProviderError,
    MarketDataService,
    market_data_service,
)


pytestmark = pytest.mark.asyncio


def sample_candles(
    ticker: str = "AAPL",
    interval: str = "1d",
    period: str = "6mo",
) -> CandleSeriesResponse:
    return CandleSeriesResponse(
        ticker=ticker,
        interval=interval,
        period=period,
        count=1,
        candles=[
            CandlePoint(
                timestamp=1_700_000_000,
                open=10.0,
                high=12.0,
                low=9.0,
                close=11.0,
                volume=100,
            )
        ],
    )


async def test_market_candles_returns_provider_data(
    ac: AsyncClient,
    auth_headers: dict[str, str],
    monkeypatch: pytest.MonkeyPatch,
):
    calls: list[tuple[str, str, str]] = []

    async def get_candles(ticker: str, interval: str, period: str):
        calls.append((ticker, interval, period))
        return sample_candles(ticker=ticker.upper(), interval=interval, period=period)

    monkeypatch.setattr(market_data_service, "get_candles", get_candles)

    response = await ac.get(
        "/market/candles/aapl?interval=1h&period=1mo",
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert response.json()["ticker"] == "AAPL"
    assert response.json()["count"] == 1
    assert response.json()["candles"][0]["close"] == 11.0
    assert calls == [("aapl", "1h", "1mo")]


async def test_market_candles_maps_missing_data_to_404(
    ac: AsyncClient,
    auth_headers: dict[str, str],
    monkeypatch: pytest.MonkeyPatch,
):
    async def missing_data(*_args, **_kwargs):
        raise MarketDataNotFoundError("No market data found.")

    monkeypatch.setattr(market_data_service, "get_candles", missing_data)

    response = await ac.get("/market/candles/UNKNOWN", headers=auth_headers)

    assert response.status_code == 404
    assert response.json()["detail"] == "No market data found."


async def test_market_candles_maps_provider_failure_to_502(
    ac: AsyncClient,
    auth_headers: dict[str, str],
    monkeypatch: pytest.MonkeyPatch,
):
    async def provider_failure(*_args, **_kwargs):
        raise MarketDataProviderError("Market provider unavailable.")

    monkeypatch.setattr(market_data_service, "get_candles", provider_failure)

    response = await ac.get("/market/candles/AAPL", headers=auth_headers)

    assert response.status_code == 502
    assert response.json()["detail"] == "Market provider unavailable."


async def test_market_candles_rejects_invalid_query_values(
    ac: AsyncClient,
    auth_headers: dict[str, str],
    monkeypatch: pytest.MonkeyPatch,
):
    async def unexpected_provider_call(**_kwargs):
        pytest.fail("The market service should not be called for invalid query values.")

    monkeypatch.setattr(
        market_data_service, "get_candles", unexpected_provider_call
    )

    response = await ac.get(
        "/market/candles/AAPL?interval=2h&period=6mo",
        headers=auth_headers,
    )
    assert response.status_code == 422


async def test_market_candles_requires_authentication(ac: AsyncClient):
    response = await ac.get("/market/candles/AAPL")
    assert response.status_code in (401, 403)


async def test_market_service_normalizes_ticker_before_fetching(
    monkeypatch: pytest.MonkeyPatch,
):
    service = MarketDataService()
    calls: list[tuple[str, str, str]] = []

    def fetch_history(ticker: str, interval: str, period: str):
        calls.append((ticker, interval, period))
        return sample_candles(interval=interval, period=period).candles

    monkeypatch.setattr(service, "_fetch_history_sync", fetch_history)

    response = await service.get_candles(" aapl ", interval="1h", period="1mo")

    assert response.ticker == "AAPL"
    assert calls == [("AAPL", "1h", "1mo")]
