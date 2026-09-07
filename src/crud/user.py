"""
用户个人资料 CRUD，ORM模型是 User（资料表），不是Main_User
"""
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from models.models import User
from schemas.user import UserCreate, UserUpdate, UserResponse


async def get_profile_by_user_id(db: AsyncSession, main_user_id: int) -> User | None:
    """
    根据登录账号id查资料（user表的user_id是外键指向main_user.id）
    """
    stmt = select(User).where(User.user_id == main_user_id)
    return await db.scalar(stmt)



async def get_profile_by_id(db: AsyncSession, u_id: int) -> User | None:
    """根据资料主键id查询"""
    stmt = select(User).where(User.id == u_id)
    return await db.scalar(stmt)



async def create_profile(db: AsyncSession, obj_in: UserCreate, main_user_id: int) -> User:
    """创建个人资料"""
    db_obj = User(
        **obj_in.model_dump(),
        user_id=main_user_id
    )
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj



async def update_profile(db: AsyncSession, db_obj: User, obj_in: UserUpdate) -> User:
    """更新个人资料"""
    update_data = obj_in.model_dump(exclude_unset=True)
    for k, v in update_data.items():
        setattr(db_obj, k, v)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj
