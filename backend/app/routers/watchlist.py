from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.crud import watchlist as crud_watchlist
from app.db.database import get_db
from app.models.user import User
from app.schemas.watchlist import (
    WatchlistCategoryCreate,
    WatchlistCategoryResponse,
    WatchlistItemCreate,
    WatchlistItemResponse,
)

router = APIRouter(prefix="/watchlists", tags=["Watchlists"])

@router.post(
    "/categories",
    response_model=WatchlistCategoryResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_watchlist_category(
    category_in: WatchlistCategoryCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new watchlist category for the authenticated user."""
    existing_category = await crud_watchlist.get_category_by_name(
        db, name=category_in.name, user_id=current_user.id
    )
    if existing_category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Watchlist category with this name already exists.",
        )

    return await crud_watchlist.create_category(
        db, category_in=category_in, user_id=current_user.id
    )

@router.get(
    "/categories",
    response_model=list[WatchlistCategoryResponse],
)
async def read_watchlist_categories(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve all watchlist categories and their tickers for the authenticated user."""
    return await crud_watchlist.get_user_categories(db, user_id=current_user.id)


@router.delete(
    "/categories/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_watchlist_category(
    category_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a watchlist category owned by the authenticated user."""
    category = await crud_watchlist.get_category_by_id(
        db, category_id=category_id, user_id=current_user.id
    )
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Watchlist category not found.",
        )

    await crud_watchlist.delete_category(db, category=category)


@router.post(
    "/categories/{category_id}/items",
    response_model=WatchlistItemResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_ticker_to_watchlist(
    category_id: int,
    item_in: WatchlistItemCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Add a ticker symbol to a specific watchlist category."""
    category = await crud_watchlist.get_category_by_id(
        db, category_id=category_id, user_id=current_user.id
    )
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Watchlist category not found.",
        )

    existing_item = await crud_watchlist.get_watchlist_item(
        db, category_id=category_id, ticker=item_in.ticker
    )
    if existing_item:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ticker '{item_in.ticker}' is already in this category.",
        )

    return await crud_watchlist.add_item_to_category(
        db, category_id=category_id, item_in=item_in
    )


@router.delete(
    "/categories/{category_id}/items/{ticker}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def remove_ticker_from_watchlist(
    category_id: int,
    ticker: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Remove a ticker symbol from a specific watchlist category."""
    category = await crud_watchlist.get_category_by_id(
        db, category_id=category_id, user_id=current_user.id
    )
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Watchlist category not found.",
        )

    item = await crud_watchlist.get_watchlist_item(
        db, category_id=category_id, ticker=ticker
    )
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticker '{ticker.upper()}' not found in this category.",
        )

    await crud_watchlist.remove_item_from_category(db, item=item)