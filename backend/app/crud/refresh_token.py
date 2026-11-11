from datetime import datetime, timedelta, timezone
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.refresh_token import RefreshToken
from app.core.config import settings

async def create_refresh_token(db: AsyncSession, user_id: int, token_str: str) -> RefreshToken:

    expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    db_token = RefreshToken(
        token = token_str,
        user_id = user_id,
        expires_at = expires_at,
        revoked = False
    )

    db.add(db_token)
    await db.commit()
    await db.refresh(db_token)

    return db_token

async def get_refresh_token(db: AsyncSession, token_str: str) -> Optional[RefreshToken]:

    result = await db.execute(
        select(RefreshToken).filter(RefreshToken.token == token_str)
    )

    return result.scalars().first()

async def revoke_refresh_token(db: AsyncSession, db_token: RefreshToken) -> None:
    db_token.revoked = True
    await db.commit() 