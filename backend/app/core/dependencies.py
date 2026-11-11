from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.database import get_db
from app.crud.user import get_user_by_username
from app.models.user import User

security_scheme = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    """FastAPI dependency to authenticate requests using JWT tokens."""
    token = credentials.credentials

    # Reusable 401 Unauthorized exception for authentication failures
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
        headers={"WWW-Authenticate": "Bearer"}
    )

    try:
        # Decode and verify token signature and validity
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )

        # Extract the username claim from the token payload
        username: str | None = payload.get("sub")
        if username is None:
            raise credentials_exception

    except JWTError:
        # Fallback for invalid signature, expired token, or malformed payload
        raise credentials_exception

    # Query the user record from the database
    user = await get_user_by_username(db, username=username)

    if user is None:
        raise credentials_exception

    # Verify that the user account is enabled
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account is inactive"
        )

    return user