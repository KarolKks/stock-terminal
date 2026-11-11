from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.schemas.user import UserCreate, UserResponse, UserLogin, Token, TokenRefreshRequest
from app.crud.user import get_user_by_email, get_user_by_username, get_user_by_id, create_user
from app.crud.refresh_token import create_refresh_token, get_refresh_token, revoke_refresh_token
from app.core.security import verify_password, create_access_token, create_refresh_token_string
from app.core.dependencies import get_current_user
from app.models.user import User

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post(
    "/register", 
    response_model=UserResponse, 
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user"
)
async def register(
    user_in: UserCreate, 
    db: AsyncSession = Depends(get_db)
):
    """Create a new user account if email and username are available."""
    # Ensure the email address is unique
    existing_email = await get_user_by_email(db, email=user_in.email)
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists."
        )

    # Ensure the username is unique
    existing_username = await get_user_by_username(db, username=user_in.username)
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this username already exists."
        )
        
    # Hash password and persist new user to database
    new_user = await create_user(db, user_in=user_in)
    return new_user


@router.post(
    "/login", 
    response_model=Token,
    summary="User login and issuance of access and refresh tokens"
)
async def login(
    credentials: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """Authenticate user credentials and issue Access & Refresh tokens."""
    user = await get_user_by_username(db, username=credentials.username)
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User account is inactive."
        )

    # Generate Access Token (JWT)
    access_token = create_access_token(data={"sub": user.username})

    # Generate and save Refresh Token in database
    refresh_token_str = create_refresh_token_string()
    await create_refresh_token(db, user_id=user.id, token_str=refresh_token_str)

    # Return both tokens
    return Token(
        access_token=access_token,
        refresh_token=refresh_token_str,
        token_type="bearer"
    )


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Fetch current logged-in user profile"
)
async def read_users_me(
    current_user: User = Depends(get_current_user)
):
    """Return profile information for the authenticated user."""
    return current_user


@router.post(
    "/refresh",
    response_model=Token,
    summary="Refresh access token using refresh token"
)
async def refresh_tokens(
    body: TokenRefreshRequest, 
    db: AsyncSession = Depends(get_db)
):
    """Validate refresh token and issue a new Access Token."""
    db_token = await get_refresh_token(db, token_str=body.refresh_token)
    if not db_token or db_token.revoked:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or revoked refresh token."
        )

    if db_token.expires_at < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has expired. Please log in again."
        )

    user = await get_user_by_id(db, user_id=db_token.user_id)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User does not exist or is inactive."
        )

    new_access_token = create_access_token(data={"sub": user.username})

    return Token(
        access_token=new_access_token,
        refresh_token=db_token.token,
        token_type="bearer"
    )


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    summary="Logout (revoke refresh token)"
)
async def logout(
    body: TokenRefreshRequest, 
    db: AsyncSession = Depends(get_db)
):
    """Revoke the refresh token in the database to log out the user."""
    db_token = await get_refresh_token(db, token_str=body.refresh_token)
    if db_token:
        await revoke_refresh_token(db, db_token)

    return {"message": "Successfully logged out."}