from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.models import Goal
from schemas.goal import GoalCreate,GoalUpdate


async def create_goal(
        db:AsyncSession,
        obj_in:GoalCreate,
        main_user_id:int
) -> Goal:
    db_obj = Goal(
        **obj_in.model_dump(),
        user_id = main_user_id
    )
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj


async def get_goal_by_id(db: AsyncSession, goal_id: int) -> Goal | None:
    """根据目标主键id查询单条目标"""
    stmt = select(Goal).where(Goal.id == goal_id)
    return await db.scalar(stmt)


async def get_all_goal(
        db:AsyncSession,
        main_user_id:int,
        skip:int = 0,
        limit:int = 100
) -> list[Goal]:
    stmt = (
            select(Goal)
            .where(Goal.user_id == main_user_id)
            .order_by(Goal.start_date.desc())
            .offset(skip)
            .limit(limit)
        )
    res = await db.execute(stmt)
    return res.scalars().all()


async def update_goal(db:AsyncSession, db_obj:Goal, obj_in:GoalUpdate) -> Goal:
    update_data = obj_in.model_dump(exclude_unset=True)
    for k,v in update_data.items():
        setattr(db_obj,k,v)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj


async def delete_goal(db: AsyncSession, db_obj: Goal) -> None:
    """删除目标，传入已经查询完成的Goal实例"""
    await db.delete(db_obj)
    await db.commit()
