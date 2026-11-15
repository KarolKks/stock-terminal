from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.watchlist import WatchlistCategory, WatchlistItem
from app.schemas.watchlist import WatchlistCategoryCreate, WatchlistItemCreate


async def get_user_categories(db: AsyncSession, user_id: int) -> list[WatchlistCategory]:
    """Retrieve all watchlist categories belonging to a specific user."""
    query = (
        select(WatchlistCategory)
        .where(WatchlistCategory.user_id == user_id)
        .options(selectinload(WatchlistCategory.items))
        .order_by(WatchlistCategory.id.asc())
    )
    result = await db.execute(query)
    return list(result.scalars().all())


async def get_category_by_id(db: AsyncSession, category_id: int, user_id: int) -> WatchlistCategory | None:
    """Retrieve a single category by ID, ensuring it belongs to the given user."""
    query = (
        select(WatchlistCategory)
        .where(
            WatchlistCategory.id == category_id,
            WatchlistCategory.user_id == user_id,
        )
        .options(selectinload(WatchlistCategory.items))
    )
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def get_category_by_name(db: AsyncSession, name: str, user_id: int) -> WatchlistCategory | None:
    """Check if the user already has a category with the same name (case-insensitive)."""
    query = select(WatchlistCategory).where(
        WatchlistCategory.user_id == user_id,
        func.lower(WatchlistCategory.name) == name.lower(),
    )
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def create_category(db: AsyncSession, category_in: WatchlistCategoryCreate, user_id: int) -> WatchlistCategory:
    """Create a new watchlist category for the user."""
    db_category = WatchlistCategory(
        name=category_in.name,
        user_id=user_id,
    )
    db.add(db_category)
    await db.commit()
    await db.refresh(db_category, attribute_names=["items"])
    return db_category


async def delete_category(db: AsyncSession, category: WatchlistCategory) -> None:
    """Delete an existing watchlist category."""
    await db.delete(category)
    await db.commit()


async def get_watchlist_item(db: AsyncSession, category_id: int, ticker: str) -> WatchlistItem | None:
    """Retrieve a specific ticker item inside a given category."""
    query = select(WatchlistItem).where(
        WatchlistItem.category_id == category_id,
        WatchlistItem.ticker == ticker.upper(),
    )
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def add_item_to_category(db: AsyncSession, category_id: int, item_in: WatchlistItemCreate) -> WatchlistItem:
    """Add a new ticker symbol to a watchlist category."""
    db_item = WatchlistItem(
        ticker=item_in.ticker,
        category_id=category_id,
    )
    db.add(db_item)
    await db.commit()
    await db.refresh(db_item)
    return db_item


async def remove_item_from_category(db: AsyncSession, item: WatchlistItem) -> None:
    """Remove a ticker item from a watchlist category."""
    await db.delete(item)
    await db.commit()