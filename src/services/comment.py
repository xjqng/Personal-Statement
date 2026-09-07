"""
评论业务层：目标存在性校验、权限校验、XSS清洗
"""
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from models.models import Main_User, Comment
from crud.comment import create_comment, get_comment_by_id, list_comment_by_target, delete_comment
from crud.diaries import get_diary_by_id
from crud.goal import get_goal_by_id
from schemas.comment import CommentCreate, CommentResponse
from core.logger import logger
from core.xxs import sanitize_html


async def create_comment_service(
    db: AsyncSession,
    data: CommentCreate,
    current_user: Main_User
) -> CommentResponse:
    # 限制只允许两种评论类型
    allow_types = {"diary", "goal"}
    if data.target_type not in allow_types:
        logger.warning(f"用户[{current_user.id}] 创建评论失败：target_type 非法={data.target_type}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"target_type只允许：{allow_types}"
        )

    # 根据类型校验目标是否真实存在
    target_exist = False
    if data.target_type == "diary":
        diary = await get_diary_by_id(db, data.target_id)
        if diary:
            target_exist = True
    elif data.target_type == "goal":
        goal = await get_goal_by_id(db, data.target_id)
        if goal:
            target_exist = True

    if not target_exist:
        logger.warning(
            f"用户[{current_user.id}] 评论不存在的目标 target_type={data.target_type}, target_id={data.target_id}"
        )
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="被评论的目标不存在")

    # XSS 清洗：评论内容为富文本，保留安全标签
    data.content = sanitize_html(data.content)

    db_obj = await create_comment(db, data, main_user_id=current_user.id)
    logger.info(
        f"用户[{current_user.id}] 创建评论成功 comment_id={db_obj.id}, target_type={data.target_type}, target_id={data.target_id}"
    )
    return CommentResponse.model_validate(db_obj)


async def get_comment_detail_service(
    db: AsyncSession,
    comment_id: int
) -> CommentResponse:
    obj = await get_comment_by_id(db, comment_id)
    if not obj:
        logger.warning(f"查询评论失败：不存在 comment_id={comment_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="评论不存在")
    logger.info(f"查询评论详情 comment_id={comment_id}")
    return CommentResponse.model_validate(obj)


async def list_target_comment_service(
    db: AsyncSession,
    target_type: str,
    target_id: int,
    skip: int = 0,
    limit: int = 100
) -> list[CommentResponse]:
    """获取某个目标(diary/goal)下所有评论，无需登录"""
    comment_list = await list_comment_by_target(db, target_type, target_id, skip, limit)
    logger.info(
        f"查询目标评论列表 target_type={target_type}, target_id={target_id}, skip={skip}, limit={limit}, 数量={len(comment_list)}"
    )
    return [CommentResponse.model_validate(item) for item in comment_list]


async def delete_comment_service(
    db: AsyncSession,
    comment_id: int,
    current_user: Main_User
) -> None:
    obj = await get_comment_by_id(db, comment_id)
    if not obj:
        logger.warning(f"用户[{current_user.id}] 删除评论失败：不存在 comment_id={comment_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="评论不存在")
    # 只能删除自己发布的评论
    if obj.user_id != current_user.id:
        logger.warning(f"用户[{current_user.id}] 越权删除他人评论 comment_id={comment_id}")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="只能删除自己的评论")
    await delete_comment(db, obj)
    logger.info(f"用户[{current_user.id}] 删除评论成功 comment_id={comment_id}")
