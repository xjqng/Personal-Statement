"""
用户个人资料业务层
"""
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from models.models import Main_User, User
from crud.user import get_profile_by_user_id, create_profile, update_profile
from schemas.user import UserCreate, UserUpdate, UserResponse
from core.logger import logger
from core.xxs import sanitize_text


async def get_my_profile_service(db: AsyncSession, current_user: Main_User) -> UserResponse:
    """查询 个人角色资料"""
    profile = await get_profile_by_user_id(db, current_user.id)
    if not profile:
        logger.warning(f"用户[{current_user.id}] 查询个人资料失败：尚未创建")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="尚未创建个人资料")
    logger.info(f"用户[{current_user.id}] 查询个人资料 profile_id={profile.id}")
    return UserResponse.model_validate(profile)


async def create_my_profile_service(
    db: AsyncSession,
    obj_in: UserCreate,
    current_user: Main_User
) -> UserResponse:
    """创建 个人角色资料"""
    # 检查是否已经存在资料（一对一，不能重复创建）
    exist = await get_profile_by_user_id(db, current_user.id)
    if exist:
        logger.warning(f"用户[{current_user.id}] 重复创建个人资料被拒")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="个人资料已存在，请勿重复创建，请使用更新接口")

    # XSS 清洗：头像URL、姓名为纯文本，全部HTML转义
    if obj_in.headshot is not None:
        obj_in.headshot = sanitize_text(obj_in.headshot)
    if obj_in.name is not None:
        obj_in.name = sanitize_text(obj_in.name)

    profile = await create_profile(db, obj_in, main_user_id=current_user.id)
    logger.info(f"用户[{current_user.id}] 创建个人资料成功 profile_id={profile.id}")
    return UserResponse.model_validate(profile)


async def update_my_profile_service(
    db: AsyncSession,
    obj_in: UserUpdate,
    current_user: Main_User
) -> UserResponse:
    """更新 个人角色资料"""
    profile = await get_profile_by_user_id(db, current_user.id)
    if not profile:
        logger.warning(f"用户[{current_user.id}] 更新个人资料失败：尚未创建")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="尚未创建个人资料")

    # XSS 清洗：仅清洗用户实际提交的字段
    if obj_in.headshot is not None:
        obj_in.headshot = sanitize_text(obj_in.headshot)
    if obj_in.name is not None:
        obj_in.name = sanitize_text(obj_in.name)

    updated = await update_profile(db, profile, obj_in)
    logger.info(f"用户[{current_user.id}] 更新个人资料成功 profile_id={updated.id}")
    return UserResponse.model_validate(updated)
