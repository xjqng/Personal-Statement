"""
用户CRUD：只做数据库操作，不做业务校验
"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.models import Main_User
from schemas.user import UserCreate
from core.security import hash_password


async def get_user_by_id(db: AsyncSession, user_id: int) -> Main_User | None:
    stmt = select(Main_User).where(Main_User.id == user_id)
    res = await db.execute(stmt)
    return res.scalar_one_or_none()


async def get_user_by_username(db: AsyncSession, username: str) -> Main_User | None:
    stmt = select(Main_User).where(Main_User.username == username)
    res = await db.execute(stmt)
    return res.scalar_one_or_none()


async def get_user_by_email(db: AsyncSession, email: str) -> Main_User | None:
    stmt = select(Main_User).where(Main_User.email == email)
    res = await db.execute(stmt)
    return res.scalar_one_or_none()


async def create_user(db: AsyncSession, obj_in: UserCreate) -> Main_User:
    db_obj = Main_User(
        username=obj_in.username,
        email=obj_in.email,
        hashed_password=hash_password(obj_in.password)
    )
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj
