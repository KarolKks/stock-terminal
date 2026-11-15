from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.market import (
    CandleSeriesResponse,
    ValidInterval,
    ValidPeriod,
)
from app.services.market_data import (
    MarketDataNotFoundError,
    MarketDataProviderError,
    market_data_service,
)

router = APIRouter(prefix="/market", tags=["Market Data"])


@router.get(
    "/candles/{ticker}",
    response_model=CandleSeriesResponse,
)
async def get_ticker_candles(
    ticker: str,
    interval: ValidInterval = Query(
        default="1d",
        description="Candlestick timeframe interval (e.g. 15m, 1h, 1d)",
    ),
    period: ValidPeriod = Query(
        default="6mo",
        description="Historical lookback period (e.g. 1mo, 6mo, 1y)",
    ),
    current_user: User = Depends(get_current_user),
):
    """Retrieve historical OHLCV candlestick data for a given ticker symbol."""
    try:
        return await market_data_service.get_candles(
            ticker=ticker,
            interval=interval,
            period=period,
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