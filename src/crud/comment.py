from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.models import Comment
from schemas.comment import CommentCreate


async def create_comment(db: AsyncSession, obj_in: CommentCreate, main_user_id: int) -> Comment:
    """创建评论，main_user_id：评论发布人的登录账号id"""
    db_obj = Comment(
        **obj_in.model_dump(),
        user_id=main_user_id
    )
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj


async def get_comment_by_id(db: AsyncSession, comment_id: int) -> Comment | None:
    """根据评论主键id查询单条评论"""
    stmt = select(Comment).where(Comment.id == comment_id)
    return await db.scalar(stmt)


async def list_comment_by_target(
    db: AsyncSession,
    target_type: str,
    target_id: int,
    skip: int = 0,
    limit: int = 100
) -> list[Comment]:
    """根据【目标类型+目标ID】查询该目标下全部评论，时间倒序"""
    stmt = (
        select(Comment)
        .where(Comment.target_type == target_type, Comment.target_id == target_id)
        .order_by(Comment.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    res = await db.execute(stmt)
    return res.scalars().all()


async def delete_comment(db: AsyncSession, db_obj: Comment) -> None:
    """删除评论，传入已经查询好的Comment实例"""
    await db.delete(db_obj)
    await db.commit()
