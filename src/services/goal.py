"""
目标业务层：存在判断、权限校验、XSS清洗
"""
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from models.models import Main_User, Goal
from crud.goal import (
    create_goal,
    get_goal_by_id,
    get_all_goal,
    update_goal,
    delete_goal
)
from schemas.goal import GoalCreate, GoalUpdate, GoalResponse
from core.logger import logger
from core.xxs import sanitize_html, sanitize_text


async def create_goal_services(
    db: AsyncSession,
    data: GoalCreate,
    current_user: Main_User
) -> GoalResponse:
    # XSS 清洗：title 纯文本，description 富文本
    data.title = sanitize_text(data.title)
    if data.description is not None:
        data.description = sanitize_html(data.description)

    obj = await create_goal(db, data, main_user_id=current_user.id)
    logger.info(f"用户[{current_user.id}] 创建目标成功 goal_id={obj.id}")
    return GoalResponse.model_validate(obj)


async def get_one_goal_svs(
    db: AsyncSession,
    goal_id: int,
    current_user: Main_User
) -> GoalResponse:
    obj = await get_goal_by_id(db, goal_id)
    if not obj:
        logger.warning(f"用户[{current_user.id}] 访问不存在的目标 goal_id={goal_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="数据不存在")
    # 权限：只能访问自己的数据
    if obj.user_id != current_user.id:
        logger.warning(f"用户[{current_user.id}] 越权访问目标 goal_id={goal_id}")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权访问")
    logger.info(f"用户[{current_user.id}] 查看目标详情 goal_id={goal_id}")
    return GoalResponse.model_validate(obj)


async def get_all_goal_svs(
    db: AsyncSession,
    current_user: Main_User,
    skip: int = 0,
    limit: int = 100
) -> list[GoalResponse]:
    obj = await get_all_goal(db, current_user.id, skip, limit)
    logger.info(f"用户[{current_user.id}] 查询目标列表 skip={skip}, limit={limit}, 数量={len(obj)}")
    return [GoalResponse.model_validate(item) for item in obj]


async def update_goal_svs(
    db: AsyncSession,
    goal_id: int,
    data: GoalUpdate,
    current_user: Main_User
) -> GoalResponse:
    obj = await get_goal_by_id(db, goal_id)
    if not obj:
        logger.warning(f"用户[{current_user.id}] 修改不存在的目标 goal_id={goal_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="数据不存在")
    if obj.user_id != current_user.id:
        logger.warning(f"用户[{current_user.id}] 越权修改目标 goal_id={goal_id}")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权修改")

    # XSS 清洗：仅清洗用户实际提交的字段
    if data.title is not None:
        data.title = sanitize_text(data.title)
    if data.description is not None:
        data.description = sanitize_html(data.description)

    updated = await update_goal(db, obj, data)
    logger.info(f"用户[{current_user.id}] 更新目标成功 goal_id={goal_id}")
    return GoalResponse.model_validate(updated)


async def delete_goal_svs(
    db: AsyncSession,
    goal_id: int,
    current_user: Main_User
) -> None:
    obj = await get_goal_by_id(db, goal_id)
    if not obj:
        logger.warning(f"用户[{current_user.id}] 删除不存在的目标 goal_id={goal_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="数据不存在")
    if obj.user_id != current_user.id:
        logger.warning(f"用户[{current_user.id}] 越权删除目标 goal_id={goal_id}")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权删除")
    await delete_goal(db, obj)
    logger.info(f"用户[{current_user.id}] 删除目标成功 goal_id={goal_id}")
