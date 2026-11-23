from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.fundamentals import (
    CompanyOverviewResponse,
    DividendHistoryResponse,
    FinancialStatementsResponse,
    StatementPeriodType,
)
from app.services.fundamentals import fundamental_data_service
from app.services.market_data import (
    MarketDataNotFoundError,
    MarketDataProviderError,
)

router = APIRouter(prefix="/market/fundamentals", tags=["Fundamentals"])


@router.get(
    "/{ticker}/overview",
    response_model=CompanyOverviewResponse,
)
async def get_company_overview(
    ticker: str,
    current_user: User = Depends(get_current_user),
):
    """Retrieve company profile, valuation multiples, and profitability metrics."""
    try:
        return await fundamental_data_service.get_overview(ticker=ticker)
    except MarketDataNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except MarketDataProviderError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc


@router.get(
    "/{ticker}/financials",
    response_model=FinancialStatementsResponse,
)
async def get_financial_statements(
    ticker: str,
    period: StatementPeriodType = Query(
        default="annual",
        description="Reporting period granularity ('annual' or 'quarterly')",
    ),
    current_user: User = Depends(get_current_user),
):
    """Retrieve multi-year or quarterly income statement, balance sheet, and cash flow data."""
    try:
        return await fundamental_data_service.get_financial_statements(
            ticker=ticker,
            period_type=period,
        )
    except MarketDataNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except MarketDataProviderError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc


@router.get(
    "/{ticker}/dividends",
    response_model=DividendHistoryResponse,
)
async def get_dividend_history(
    ticker: str,
    current_user: User = Depends(get_current_user),
):
    """Retrieve multi-year dividend payouts per share and year-over-year growth."""
    try:
        return await fundamental_data_service.get_dividend_history(ticker=ticker)
    except MarketDataNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except MarketDataProviderError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc