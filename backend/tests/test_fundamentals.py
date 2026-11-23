from types import SimpleNamespace

import pandas as pd
import pytest
from httpx import AsyncClient

from app.schemas.fundamentals import (
    CompanyOverviewResponse,
    DividendHistoryResponse,
    FinancialStatementPeriod,
    FinancialStatementsResponse,
)
from app.services.fundamentals import FundamentalDataService, fundamental_data_service
from app.services.market_data import (
    MarketDataNotFoundError,
    MarketDataProviderError,
)

pytestmark = pytest.mark.asyncio


async def test_fundamentals_overview_returns_provider_data(
    ac: AsyncClient,
    auth_headers: dict[str, str],
    monkeypatch: pytest.MonkeyPatch,
):
    expected = CompanyOverviewResponse(ticker="AAPL", name="Apple")
    calls: list[str] = []

    async def get_overview(ticker: str):
        calls.append(ticker)
        return expected

    monkeypatch.setattr(fundamental_data_service, "get_overview", get_overview)

    response = await ac.get(
        "/market/fundamentals/aapl/overview",
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert response.json()["ticker"] == "AAPL"
    assert response.json()["name"] == "Apple"
    assert calls == ["aapl"]


async def test_fundamentals_financials_passes_period_to_service(
    ac: AsyncClient,
    auth_headers: dict[str, str],
    monkeypatch: pytest.MonkeyPatch,
):
    expected = FinancialStatementsResponse(
        ticker="AAPL",
        period_type="quarterly",
        statements=[FinancialStatementPeriod(period_end="2025-03-31", total_revenue=10)],
    )
    calls: list[tuple[str, str]] = []

    async def get_financial_statements(ticker: str, period_type: str):
        calls.append((ticker, period_type))
        return expected

    monkeypatch.setattr(
        fundamental_data_service,
        "get_financial_statements",
        get_financial_statements,
    )

    response = await ac.get(
        "/market/fundamentals/aapl/financials?period=quarterly",
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert response.json()["period_type"] == "quarterly"
    assert response.json()["statements"][0]["total_revenue"] == 10
    assert calls == [("aapl", "quarterly")]


async def test_fundamentals_dividends_returns_provider_data(
    ac: AsyncClient,
    auth_headers: dict[str, str],
    monkeypatch: pytest.MonkeyPatch,
):
    expected = DividendHistoryResponse(ticker="AAPL", history=[])
    calls: list[str] = []

    async def get_dividend_history(ticker: str):
        calls.append(ticker)
        return expected

    monkeypatch.setattr(
        fundamental_data_service,
        "get_dividend_history",
        get_dividend_history,
    )

    response = await ac.get(
        "/market/fundamentals/aapl/dividends",
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert response.json() == {"ticker": "AAPL", "currency": None, "history": []}
    assert calls == ["aapl"]


@pytest.mark.parametrize(
    ("path", "service_method"),
    [
        ("/market/fundamentals/AAPL/overview", "get_overview"),
        ("/market/fundamentals/AAPL/financials", "get_financial_statements"),
        ("/market/fundamentals/AAPL/dividends", "get_dividend_history"),
    ],
)
@pytest.mark.parametrize(
    ("error", "expected_status"),
    [
        (MarketDataNotFoundError("Ticker not found."), 404),
        (MarketDataProviderError("Provider unavailable."), 502),
    ],
)
async def test_fundamentals_maps_provider_errors(
    ac: AsyncClient,
    auth_headers: dict[str, str],
    monkeypatch: pytest.MonkeyPatch,
    path: str,
    service_method: str,
    error: Exception,
    expected_status: int,
):
    async def fail(*_args, **_kwargs):
        raise error

    monkeypatch.setattr(fundamental_data_service, service_method, fail)

    response = await ac.get(path, headers=auth_headers)

    assert response.status_code == expected_status
    assert response.json()["detail"] == str(error)


async def test_fundamentals_requires_authentication(ac: AsyncClient):
    response = await ac.get("/market/fundamentals/AAPL/overview")
    assert response.status_code in (401, 403)


async def test_fundamentals_rejects_invalid_financial_period(
    ac: AsyncClient,
    auth_headers: dict[str, str],
    monkeypatch: pytest.MonkeyPatch,
):
    async def unexpected_provider_call(*_args, **_kwargs):
        pytest.fail("The fundamentals service should not be called for an invalid period.")

    monkeypatch.setattr(
        fundamental_data_service,
        "get_financial_statements",
        unexpected_provider_call,
    )

    response = await ac.get(
        "/market/fundamentals/AAPL/financials?period=monthly",
        headers=auth_headers,
    )

    assert response.status_code == 422


async def test_fundamentals_overview_normalizes_ticker_and_ratios(
    monkeypatch: pytest.MonkeyPatch,
):
    service = FundamentalDataService()
    monkeypatch.setattr(
        "app.services.fundamentals.yf.Ticker",
        lambda ticker: SimpleNamespace(
            info={
                "longName": "Apple Inc.",
                "marketCap": 1_234_567,
                "trailingAnnualDividendYield": 0.0345,
                "returnOnEquity": 0.245,
            }
        ),
    )

    response = await service.get_overview(" aapl ")

    assert response.ticker == "AAPL"
    assert response.name == "Apple Inc."
    assert response.market_cap == 1_234_567
    assert response.dividend_yield == 3.45
    assert response.roe == 24.5


async def test_fundamentals_financials_selects_period_and_normalizes_values(
    monkeypatch: pytest.MonkeyPatch,
):
    service = FundamentalDataService()
    date = pd.Timestamp("2025-03-31")
    selected: list[str] = []
    income = pd.DataFrame({"value": [100.0]}, index=["Total Revenue"]).rename(
        columns={"value": date}
    )
    balance = pd.DataFrame({"value": [50.0]}, index=["Total Assets"]).rename(
        columns={"value": date}
    )
    cashflow = pd.DataFrame({"value": [-12.0]}, index=["Capital Expenditure"]).rename(
        columns={"value": date}
    )

    class FakeTicker:
        fast_info = {"currency": "USD"}

        @property
        def quarterly_income_stmt(self):
            selected.append("quarterly_income_stmt")
            return income

        @property
        def quarterly_balance_sheet(self):
            selected.append("quarterly_balance_sheet")
            return balance

        @property
        def quarterly_cashflow(self):
            selected.append("quarterly_cashflow")
            return cashflow

    monkeypatch.setattr(
        "app.services.fundamentals.yf.Ticker",
        lambda ticker: FakeTicker(),
    )

    response = await service.get_financial_statements(" msft ", "quarterly")

    assert response.ticker == "MSFT"
    assert response.period_type == "quarterly"
    assert response.currency == "USD"
    assert selected == [
        "quarterly_income_stmt",
        "quarterly_balance_sheet",
        "quarterly_cashflow",
    ]
    assert response.statements[0].period_end == "2025-03-31"
    assert response.statements[0].total_revenue == 100
    assert response.statements[0].total_assets == 50
    assert response.statements[0].capital_expenditure == 12


async def test_fundamentals_dividends_aggregates_years_and_calculates_growth(
    monkeypatch: pytest.MonkeyPatch,
):
    service = FundamentalDataService()
    dividends = pd.Series(
        [1.0, 1.5, 2.0],
        index=pd.to_datetime(["2023-02-01", "2023-08-01", "2024-06-01"]),
    )
    monkeypatch.setattr(
        "app.services.fundamentals.yf.Ticker",
        lambda ticker: SimpleNamespace(
            dividends=dividends,
            fast_info={"currency": "USD"},
        ),
    )

    response = await service.get_dividend_history(" aapl ")

    assert response.ticker == "AAPL"
    assert response.currency == "USD"
    assert [
        (
            point.year,
            point.total_dividend_per_share,
            point.payouts_count,
            point.yoy_change_pct,
        )
        for point in response.history
    ] == [
        (2024, 2.0, 1, -20.0),
        (2023, 2.5, 2, None),
    ]
