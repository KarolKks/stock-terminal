from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.database import Base

class WatchlistCategory(Base):
    __tablename__ = "watchlist_categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable = False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable = False)

    owner = relationship("User", back_populates = "watchlist_categories")
    items = relationship(
        "WatchlistItem",
        back_populates = "category",
        cascade = "all, delete-orphan",
        lazy = "selectin",
    )

class WatchlistItem(Base):
    __tablename__ = "watchlist_items"

    id = Column(Integer, primary_key = True, index = True)
    ticker = Column(String(20), nullable = False, index = True)
    category_id = Column(Integer, ForeignKey("watchlist_categories.id", ondelete="CASCADE"), nullable=False)
    added_at = Column(DateTime(timezone=True), server_default=func.now())

    category = relationship("WatchlistCategory", back_populates = "items")

    __table_args__ = (
        UniqueConstraint("category_id", "ticker", name = "uq_category_ticker"),
    )
