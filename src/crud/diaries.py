"""
日记模块CRUD，仅做数据库操作，无业务、权限判断
"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.models import Diary
from schemas.diaries import DiaryCreate, DiaryUpdate


async def create_diary(db: AsyncSession, obj_in: DiaryCreate, main_user_id: int) -> Diary:
    """创建单条日记，main_user_id为登录账号Main_User的id"""
    db_obj = Diary(
        **obj_in.model_dump(),
        user_id=main_user_id
    )
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj


async def get_diary_by_id(db: AsyncSession, diary_id: int) -> Diary | None:
    """根据日记主键ID查询单条日记，找不到返回None"""
    stmt = select(Diary).where(Diary.id == diary_id)
    return await db.scalar(stmt)


async def list_diaries_by_user_id(
    db: AsyncSession,
    main_user_id: int,
    skip: int = 0,
    limit: int = 100
) -> list[Diary]:
    """查询某一个用户的全部日记，分页，按创建时间倒序"""
    stmt = (
        select(Diary)
        .where(Diary.user_id == main_user_id)
        .order_by(Diary.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    res = await db.execute(stmt)
    return res.scalars().all()


async def update_diary(db: AsyncSession, db_obj: Diary, obj_in: DiaryUpdate) -> Diary:
    """
    更新日记（局部更新 exclude_unset）
    注意：传入已经查询完成的Diary实例，crud内部不再做查询
    """
    update_data = obj_in.model_dump(exclude_unset=True)
    for k, v in update_data.items():
        setattr(db_obj, k, v)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj


async def delete_diary(db: AsyncSession, db_obj: Diary) -> None:
    """
    删除日记
    注意：传入已经查询完成的Diary实例，crud内部不再做查询
    """
    await db.delete(db_obj)
    await db.commit()
