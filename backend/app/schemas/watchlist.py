from datetime import datetime
import re
from pydantic import BaseModel, ConfigDict, Field, field_validator


class WatchlistItemCreate(BaseModel):
    ticker: str = Field(..., min_length=1, max_length=20, examples=["AAPL"])

    @field_validator("ticker")
    @classmethod
    def normalize_and_validate_ticker(cls, value: str) -> str:
        cleaned = value.strip().upper()
        if not cleaned:
            raise ValueError("Ticker symbol cannot be empty.")
        if not re.match(r"^[A-Z0-9.\-^=]+$", cleaned):
            raise ValueError("Ticker symbol contains invalid characters.")
        return cleaned


class WatchlistItemResponse(BaseModel):
    id: int
    ticker: str
    category_id: int
    added_at: datetime

    model_config = ConfigDict(from_attributes=True)


class WatchlistCategoryCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50, examples=["Tech Stocks"])

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Category name cannot be empty.")
        return cleaned


class WatchlistCategoryUpdate(WatchlistCategoryCreate):
    pass


class WatchlistCategoryResponse(BaseModel):
    id: int
    name: str
    user_id: int
    items: list[WatchlistItemResponse] = []

    model_config = ConfigDict(from_attributes=True)