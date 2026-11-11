from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.schemas.user import UserCreate, UserResponse, UserLogin, Token
from app.crud.user import get_user_by_email, get_user_by_username, create_user
from app.core.security import verify_password, create_access_token
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
async def register( user_in: UserCreate, db: AsyncSession = Depends(get_db) ):
    """Create a new user account if email and username are available."""
    # Ensure the email address is unique
    existing_email = await get_user_by_email(db, email=user_in.email)
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )

    # Ensure the username is unique
    existing_username = await get_user_by_username(db, username=user_in.username)
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this username already exists"
        )
        
    # Hash password and persist new user to database
    new_user = await create_user(db, user_in=user_in)
    return new_user
    

@router.post(
    "/login", 
    response_model=Token,
    summary="User login and JWT token issuance"
)
async def login(credentials: UserLogin, db: AsyncSession = Depends(get_db)):
    """Authenticate user credentials and issue an access token."""
    user = await get_user_by_username(db, username=credentials.username)
    
    # Generic credential check prevents username enumeration attacks
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Prevent authentication for disabled accounts
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account is inactive"
        )

    # Issue JWT token containing username claim
    access_token = create_access_token(data={"sub": user.username})
    return Token(access_token=access_token, token_type="bearer")


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Fetch current logged-in user profile"
)
async def read_users_me(
    current_user: User = Depends(get_current_user)
):
    """Return profile information for the authenticated request user."""
    return current_user