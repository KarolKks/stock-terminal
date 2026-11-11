from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, Boolean, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)

    email: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)

    first_name: Mapped[str] = mapped_column(String(50), nullable=False)

    last_name: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")