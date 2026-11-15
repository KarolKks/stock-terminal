import asyncio
import pandas as pd
import yfinance as yf

from app.schemas.market import (
    CandlePoint,
    CandleSeriesResponse,
    ValidInterval,
    ValidPeriod,
)


class MarketDataNotFoundError(Exception):
    """Raised when a ticker does not exist or has no data for the given range."""


class MarketDataProviderError(Exception):
    """Raised when the external market data provider fails unexpectedly."""


class MarketDataService:
    def _fetch_history_sync(
        self,
        ticker: str,
        interval: ValidInterval,
        period: ValidPeriod,
    ) -> list[CandlePoint]:
        """Synchronous wrapper around yfinance history download."""
        try:

            stock = yf.Ticker(ticker)
            df = stock.history(period=period, interval=interval)

        except Exception as exc:

            raise MarketDataProviderError(
                f"Failed to fetch data from market provider for '{ticker}'."
            ) from exc

        if df is None or df.empty:

            raise MarketDataNotFoundError(
                f"No market data found for '{ticker}' (check symbol or interval/period combination)."
            )

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        df = df.dropna(subset=["Open", "High", "Low", "Close"])
        if df.empty:

            raise MarketDataNotFoundError(
                f"No valid OHLC data points available for '{ticker}'."
            )

        candles: list[CandlePoint] = []

        for idx, row in df.iterrows():

            ts_seconds = int(idx.timestamp())
            raw_volume = row.get("Volume")
            volume = 0 if pd.isna(raw_volume) else int(raw_volume)

            candles.append(

                CandlePoint(
                    timestamp=ts_seconds,
                    open=round(float(row["Open"]), 4),
                    high=round(float(row["High"]), 4),
                    low=round(float(row["Low"]), 4),
                    close=round(float(row["Close"]), 4),
                    volume=volume,
                )

            )

        return candles

    async def get_candles(
            
        self,
        ticker: str,
        interval: ValidInterval = "1d",
        period: ValidPeriod = "6mo",
        
    ) -> CandleSeriesResponse:
        """Asynchronously fetch and format OHLCV candlestick data."""

        clean_ticker = ticker.strip().upper()

        candles = await asyncio.to_thread(
            self._fetch_history_sync,
            clean_ticker,
            interval,
            period,
        )

        return CandleSeriesResponse(
            ticker=clean_ticker,
            interval=interval,
            period=period,
            count=len(candles),
            candles=candles,
        )

    async def ticker_exists(self, ticker: str) -> bool:
        """Check whether a ticker symbol returns valid recent market data."""
        clean_ticker = ticker.strip().upper()

        try:
            
            candles = await asyncio.to_thread(
                self._fetch_history_sync,
                clean_ticker,
                "1d",
                "5d",
            )
            return len(candles) > 0
        except (MarketDataNotFoundError, MarketDataProviderError):
            return False


market_data_service = MarketDataService()