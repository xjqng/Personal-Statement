"""
用户认证service层，只写业务逻辑，数据库操作全部调用crud
"""
from typing import Tuple
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from core.security import verify_token
from crud.auth import get_user_by_username, get_user_by_email, create_user, get_user_by_id
from schemas.main_user import UserCreate
from models.models import Main_User
from core.security import verify_password, create_access_token, create_refresh_token
from core.config import settings
from core.logger import logger
from core.xxs import sanitize_html,sanitize_text



async def register_user_service(db: AsyncSession, data: UserCreate) -> Main_User:

    safe_username = sanitize_text(data.username)
    safe_email = sanitize_text(data.email)
    data.username = safe_username
    data.email = safe_email
    # 业务校验
    exist_name = await get_user_by_username(db, data.username)
    if exist_name:
        logger.warning(f"注册失败，用户名已占用 username={data.username}")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="用户名已被占用")

    exist_email = await get_user_by_email(db, data.email)
    if exist_email:
        logger.warning(f"注册失败，邮箱已被注册 email={data.email}")
        raise HTTPException(status_code=400, detail="邮箱已被注册")

    # 调用crud创建用户
    user = await create_user(db, data)
    logger.info(f"新用户注册成功 user_id={user.id}, username={user.username}")
    return user


async def authenticate_user_service(db: AsyncSession, username: str, password: str):

    user = await get_user_by_username(db, username)
    if not user:
        logger.warning(f"登录校验失败，用户名不存在 username={username}")
        return None, "用户名或密码错误"
    
    if not user.is_active:
        logger.warning(f"登录校验失败，账号被禁用 username={username}, user_id={user.id}")
        return None, "账户已被禁用"
    
    if not verify_password(password, user.hashed_password):
        logger.warning(f"登录校验失败，密码错误 username={username}, user_id={user.id}")
        return None, "用户名或密码错误"
    return user, None


async def login_user_service(db: AsyncSession, username: str, password: str) -> dict:
    user, err = await authenticate_user_service(db, username, password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=err)

    token_payload = {"sub": str(user.id), "username": user.username}
    access_token = create_access_token(token_payload)
    refresh_token = create_refresh_token(token_payload)
    logger.info(f"用户登录成功 user_id={user.id}, username={user.username}")
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }


async def refresh_token_service(db: AsyncSession, refresh_token: str) -> dict:

    payload = verify_token(refresh_token, expected_type="refresh")

    if not payload:
        logger.warning("刷新token失败：无效或者过期的refresh_token")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="无效或过期的刷新令牌")
    
    user_id = payload.get("sub")

    if not user_id:
        logger.warning("刷新token失败，token payload缺少sub字段")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="令牌数据无效")
    
    user = await get_user_by_id(db, int(user_id))
    
    if not user or not user.is_active:
        logger.warning(f"刷新token失败，用户不存在或已禁用 user_id={user_id}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户不存在或已禁用")
    token_payload = {"sub": str(user.id), "username": user.username}
    access_token = create_access_token(token_payload)
    logger.info(f"用户刷新访问令牌成功 user_id={user.id}")
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }