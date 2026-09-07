from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, field_validator


class UserCreate(BaseModel):
    username: str = Field(
            min_length=3,
            max_length=50
        )
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    username: str = Field(
                min_length=1,
                max_length=50
            )
    email: str
    hashed_password: str



class TokenResponse(BaseModel):
    """
    JWT令牌响应Schema
    """
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int


class RefreshTokenRequest(BaseModel):
    """
    刷新令牌请求Schema
    """
    refresh_token: str = Field(description="刷新令牌")

    