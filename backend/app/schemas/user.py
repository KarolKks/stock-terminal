from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict

class UserBase(BaseModel):
    username: str
    email: EmailStr
    first_name: str
    last_name: Optional[str] = None

# shema from user register, userBase + password
class UserCreate(UserBase):
    password: str

# shema from user logging
class UserLogin(BaseModel):
    username: str
    password: str

# shema returned by api upon creation or retrieval of a accounts
class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# return shema after correct logging
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenRefreshRequest(BaseModel):
    refresh_token: str