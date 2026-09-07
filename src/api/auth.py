"""
用户认证api，格式完全对齐task业务模板
"""
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from db.session import get_db
from schemas.main_user import UserCreate, TokenResponse, RefreshTokenRequest
from services.auth import register_user_service, login_user_service, refresh_token_service

router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/register", response_model=TokenResponse)
async def register(
    data: UserCreate,
    db: AsyncSession = Depends(get_db)
):

    user = await register_user_service(db, data)
    return await login_user_service(db, user.username, data.password)


@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    return await login_user_service(db, form_data.username, form_data.password)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    req: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    return await refresh_token_service(db, req.refresh_token)