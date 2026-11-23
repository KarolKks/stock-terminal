import asyncio
import math
import pandas as pd
import yfinance as yf

from app.schemas.fundamentals import (
    AnnualDividendPoint,
    CompanyOverviewResponse,
    DividendHistoryResponse,
    FinancialStatementPeriod,
    FinancialStatementsResponse,
    StatementPeriodType,
)
from app.services.market_data import (
    MarketDataNotFoundError,
    MarketDataProviderError,
)


class FundamentalDataService:
    @staticmethod
    def _to_float(value: object, decimals: int = 2) -> float | None:
        """Safely convert a value to float, filtering out None and NaN."""
        if value is None:
            return None
        try:
            num = float(value)
            if math.isnan(num) or math.isinf(num):
                return None
            return round(num, decimals)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _to_int(value: object) -> int | None:
        """Safely convert a value to int, filtering out None and NaN."""
        if value is None:
            return None
        try:
            num = float(value)
            if math.isnan(num) or math.isinf(num):
                return None
            return int(round(num))
        except (TypeError, ValueError):
            return None

    @classmethod
    def _ratio_to_pct(cls, value: object, decimals: int = 2) -> float | None:
        """Convert a decimal ratio (e.g. 0.245) to percentage points (24.5)."""
        num = cls._to_float(value, decimals=decimals + 2)
        if num is None:
            return None
        return round(num * 100, decimals)

    @classmethod
    def _extract_statement_value(
        cls,
        df: pd.DataFrame | None,
        column: object,
        row_candidates: list[str],
        absolute: bool = False,
    ) -> float | None:
        """Extract a numeric value from a financial statement DataFrame using fallback row names."""
        if df is None or df.empty or column not in df.columns:
            return None

        for row_name in row_candidates:
            if row_name in df.index:
                val = cls._to_float(df.loc[row_name, column], decimals=2)
                if val is not None:
                    return abs(val) if absolute else val
        return None

    def _fetch_overview_sync(self, ticker: str) -> CompanyOverviewResponse:
        """Synchronous wrapper to fetch company profile and valuation multiples."""
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
        except Exception as exc:
            raise MarketDataProviderError(
                f"Failed to fetch fundamental overview for '{ticker}'."
            ) from exc

        if not info or (
            not info.get("shortName")
            and not info.get("longName")
            and not info.get("regularMarketPrice")
            and not info.get("currentPrice")
        ):
            raise MarketDataNotFoundError(
                f"No fundamental data found for ticker '{ticker}'."
            )

        # Yahoo Finance returns dividendYield already in % (e.g. 3.45),
        # while trailingAnnualDividendYield is a decimal ratio (0.0345).
        dividend_yield = self._to_float(info.get("dividendYield"), decimals=2)
        if dividend_yield is None:
            dividend_yield = self._ratio_to_pct(
                info.get("trailingAnnualDividendYield"), decimals=2
            )

        return CompanyOverviewResponse(
            ticker=ticker,
            name=info.get("longName") or info.get("shortName"),
            exchange=info.get("exchange"),
            currency=info.get("financialCurrency") or info.get("currency"),
            sector=info.get("sector"),
            industry=info.get("industry"),
            website=info.get("website"),
            employees=self._to_int(info.get("fullTimeEmployees")),
            description=info.get("longBusinessSummary"),
            market_cap=self._to_int(info.get("marketCap")),
            pe_ratio=self._to_float(info.get("trailingPE")),
            forward_pe=self._to_float(info.get("forwardPE")),
            pb_ratio=self._to_float(info.get("priceToBook")),
            ps_ratio=self._to_float(info.get("priceToSalesTrailing12Months")),
            ev_to_ebitda=self._to_float(info.get("enterpriseToEbitda")),
            eps=self._to_float(info.get("trailingEps")),
            dividend_yield=dividend_yield,
            roe=self._ratio_to_pct(info.get("returnOnEquity")),
            roa=self._ratio_to_pct(info.get("returnOnAssets")),
            profit_margin=self._ratio_to_pct(info.get("profitMargins")),
            operating_margin=self._ratio_to_pct(info.get("operatingMargins")),
            debt_to_equity=self._to_float(info.get("debtToEquity")),
            current_ratio=self._to_float(info.get("currentRatio")),
        )

    def _fetch_statements_sync(
        self,
        ticker: str,
        period_type: StatementPeriodType,
    ) -> FinancialStatementsResponse:
        """Synchronous wrapper to fetch multi-year or quarterly financial statements."""
        try:
            stock = yf.Ticker(ticker)
            if period_type == "quarterly":
                income_df = stock.quarterly_income_stmt
                balance_df = stock.quarterly_balance_sheet
                cashflow_df = stock.quarterly_cashflow
            else:
                income_df = stock.income_stmt
                balance_df = stock.balance_sheet
                cashflow_df = stock.cashflow

            currency = None
            try:
                currency = stock.fast_info.get("currency")
            except Exception:
                currency = None
        except Exception as exc:
            raise MarketDataProviderError(
                f"Failed to fetch financial statements for '{ticker}'."
            ) from exc

        all_dates = set()
        for df in (income_df, balance_df, cashflow_df):
            if df is not None and not df.empty:
                all_dates.update(df.columns.tolist())

        if not all_dates:
            raise MarketDataNotFoundError(
                f"No financial statements available for ticker '{ticker}'."
            )

        sorted_dates = sorted(all_dates, reverse=True)
        statements: list[FinancialStatementPeriod] = []

        for col_date in sorted_dates:
            period_label = (
                col_date.strftime("%Y-%m-%d")
                if hasattr(col_date, "strftime")
                else str(col_date)[:10]
            )

            statements.append(
                FinancialStatementPeriod(
                    period_end=period_label,
                    # Income Statement
                    total_revenue=self._extract_statement_value(
                        income_df, col_date, ["Total Revenue", "Operating Revenue"]
                    ),
                    gross_profit=self._extract_statement_value(
                        income_df, col_date, ["Gross Profit"]
                    ),
                    operating_income=self._extract_statement_value(
                        income_df, col_date, ["Operating Income", "EBIT"]
                    ),
                    ebitda=self._extract_statement_value(
                        income_df, col_date, ["EBITDA", "Normalized EBITDA"]
                    ),
                    net_income=self._extract_statement_value(
                        income_df,
                        col_date,
                        ["Net Income", "Net Income Common Stockholders"],
                    ),
                    eps=self._extract_statement_value(
                        income_df, col_date, ["Diluted EPS", "Basic EPS"]
                    ),
                    # Balance Sheet
                    total_assets=self._extract_statement_value(
                        balance_df, col_date, ["Total Assets"]
                    ),
                    total_liabilities=self._extract_statement_value(
                        balance_df,
                        col_date,
                        [
                            "Total Liabilities Net Minority Interest",
                            "Total Liabilities",
                        ],
                    ),
                    total_equity=self._extract_statement_value(
                        balance_df,
                        col_date,
                        [
                            "Stockholders Equity",
                            "Total Equity Gross Minority Interest",
                            "Common Stock Equity",
                        ],
                    ),
                    cash_and_equivalents=self._extract_statement_value(
                        balance_df,
                        col_date,
                        [
                            "Cash And Cash Equivalents",
                            "Cash Cash Equivalents And Short Term Investments",
                        ],
                    ),
                    total_debt=self._extract_statement_value(
                        balance_df, col_date, ["Total Debt"]
                    ),
                    # Cash Flow
                    operating_cash_flow=self._extract_statement_value(
                        cashflow_df,
                        col_date,
                        ["Operating Cash Flow", "Cash Flow From Continuing Operating Activities"],
                    ),
                    capital_expenditure=self._extract_statement_value(
                        cashflow_df,
                        col_date,
                        ["Capital Expenditure"],
                        absolute=True,
                    ),
                    free_cash_flow=self._extract_statement_value(
                        cashflow_df, col_date, ["Free Cash Flow"]
                    ),
                    dividends_paid=self._extract_statement_value(
                        cashflow_df,
                        col_date,
                        ["Cash Dividends Paid", "Common Stock Dividend Paid"],
                        absolute=True,
                    ),
                )
            )

        return FinancialStatementsResponse(
            ticker=ticker,
            period_type=period_type,
            currency=currency,
            statements=statements,
        )

    def _fetch_dividends_sync(self, ticker: str) -> DividendHistoryResponse:
        """Synchronous wrapper to fetch multi-year dividend payouts and YoY growth."""
        try:
            stock = yf.Ticker(ticker)
            dividends_series = stock.dividends
            currency = None
            try:
                currency = stock.fast_info.get("currency")
            except Exception:
                currency = None
        except Exception as exc:
            raise MarketDataProviderError(
                f"Failed to fetch dividend history for '{ticker}'."
            ) from exc

        if dividends_series is None or dividends_series.empty:
            # Verify whether the ticker exists at all or simply pays no dividends
            try:
                hist = stock.history(period="5d", interval="1d")
            except Exception as exc:
                raise MarketDataProviderError(
                    f"Failed to verify ticker '{ticker}'."
                ) from exc

            if hist is None or hist.empty:
                raise MarketDataNotFoundError(
                    f"Ticker '{ticker}' was not found on market exchanges."
                )

            return DividendHistoryResponse(
                ticker=ticker,
                currency=currency,
                history=[],
            )

        yearly_totals: dict[int, float] = {}
        yearly_counts: dict[int, int] = {}

        for idx, amount in dividends_series.items():
            clean_amount = self._to_float(amount, decimals=4)
            if clean_amount is None or clean_amount <= 0:
                continue
            year = int(idx.year)
            yearly_totals[year] = yearly_totals.get(year, 0.0) + clean_amount
            yearly_counts[year] = yearly_counts.get(year, 0) + 1

        # Calculate YoY change in chronological order (oldest -> newest)
        sorted_years_asc = sorted(yearly_totals.keys())
        points_asc: list[AnnualDividendPoint] = []
        prev_total: float | None = None

        for year in sorted_years_asc:
            total = round(yearly_totals[year], 4)
            yoy_pct: float | None = None
            if prev_total is not None and prev_total > 0:
                yoy_pct = round(((total - prev_total) / prev_total) * 100, 2)

            points_asc.append(
                AnnualDividendPoint(
                    year=year,
                    total_dividend_per_share=total,
                    payouts_count=yearly_counts[year],
                    yoy_change_pct=yoy_pct,
                )
            )
            prev_total = total

        # Return newest years first to match financial statements ordering
        points_desc = list(reversed(points_asc))

        return DividendHistoryResponse(
            ticker=ticker,
            currency=currency,
            history=points_desc,
        )

    async def get_overview(self, ticker: str) -> CompanyOverviewResponse:
        """Asynchronously fetch company overview and key valuation ratios."""
        clean_ticker = ticker.strip().upper()
        return await asyncio.to_thread(self._fetch_overview_sync, clean_ticker)

    async def get_financial_statements(
        self,
        ticker: str,
        period_type: StatementPeriodType = "annual",
    ) -> FinancialStatementsResponse:
        """Asynchronously fetch multi-year or quarterly financial statements."""
        clean_ticker = ticker.strip().upper()
        return await asyncio.to_thread(
            self._fetch_statements_sync,
            clean_ticker,
            period_type,
        )

    async def get_dividend_history(self, ticker: str) -> DividendHistoryResponse:
        """Asynchronously fetch multi-year dividend history with YoY growth."""
        clean_ticker = ticker.strip().upper()
        return await asyncio.to_thread(self._fetch_dividends_sync, clean_ticker)


fundamental_data_service = FundamentalDataService()