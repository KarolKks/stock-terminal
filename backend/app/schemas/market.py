from typing import Literal
from pydantic import BaseModel, Field

ValidInterval = Literal["1m", "5m", "15m", "30m", "1h", "1d", "1wk", "1mo"]
ValidPeriod = Literal["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "ytd", "max"]


class CandlePoint(BaseModel):
    timestamp: int = Field(..., description="Unix timestamp in seconds (UTC)")
    open: float
    high: float
    low: float
    close: float
    volume: int


class CandleSeriesResponse(BaseModel):
    ticker: str
    interval: ValidInterval
    period: ValidPeriod
    count: int
    candles: list[CandlePoint]