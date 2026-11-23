from typing import Literal
from pydantic import BaseModel, Field

StatementPeriodType = Literal["annual", "quarterly"]


class CompanyOverviewResponse(BaseModel):
    ticker: str
    name: str | None = None
    exchange: str | None = None
    currency: str | None = None
    sector: str | None = None
    industry: str | None = None
    website: str | None = None
    employees: int | None = None
    description: str | None = None

    # Valuation metrics
    market_cap: int | None = None
    pe_ratio: float | None = Field(default=None, description="Trailing P/E (C/Z)")
    forward_pe: float | None = Field(default=None, description="Forward P/E")
    pb_ratio: float | None = Field(default=None, description="Price to Book (C/WK)")
    ps_ratio: float | None = Field(default=None, description="Price to Sales (C/P)")
    ev_to_ebitda: float | None = None
    eps: float | None = Field(default=None, description="Trailing Earnings Per Share")

    # Profitability, dividends, and debt
    dividend_yield: float | None = Field(default=None, description="Dividend yield in %")
    roe: float | None = Field(default=None, description="Return on Equity in %")
    roa: float | None = Field(default=None, description="Return on Assets in %")
    profit_margin: float | None = Field(default=None, description="Net profit margin in %")
    operating_margin: float | None = Field(default=None, description="Operating margin in %")
    debt_to_equity: float | None = None
    current_ratio: float | None = None


class FinancialStatementPeriod(BaseModel):
    period_end: str = Field(..., description="Reporting period end date (YYYY-MM-DD)")

    # Income Statement
    total_revenue: float | None = None
    gross_profit: float | None = None
    operating_income: float | None = None
    ebitda: float | None = None
    net_income: float | None = None
    eps: float | None = Field(default=None, description="Diluted EPS for the period")

    # Balance Sheet
    total_assets: float | None = None
    total_liabilities: float | None = None
    total_equity: float | None = None
    cash_and_equivalents: float | None = None
    total_debt: float | None = None

    # Cash Flow
    operating_cash_flow: float | None = None
    capital_expenditure: float | None = None
    free_cash_flow: float | None = None
    dividends_paid: float | None = Field(
        default=None,
        description="Total cash dividends paid in the period",
    )


class FinancialStatementsResponse(BaseModel):
    ticker: str
    period_type: StatementPeriodType
    currency: str | None = None
    statements: list[FinancialStatementPeriod]


class AnnualDividendPoint(BaseModel):
    year: int
    total_dividend_per_share: float = Field(
        ...,
        description="Sum of dividends paid per share in a given calendar year",
    )
    payouts_count: int = Field(
        ...,
        description="Number of dividend payouts in that year (e.g. 4 for quarterly, 1 for GPW)",
    )
    yoy_change_pct: float | None = Field(
        default=None,
        description="Percentage change compared to the previous year",
    )


class DividendHistoryResponse(BaseModel):
    ticker: str
    currency: str | None = None
    history: list[AnnualDividendPoint]