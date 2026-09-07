from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from db.session import get_db
from api.deps import get_current_user
from models.models import Main_User
from schemas.goal import GoalCreate,GoalUpdate,GoalResponse
from services.goal import (
    create_goal_services,
    get_all_goal_svs,
    get_one_goal_svs,
    update_goal_svs,
    delete_goal_svs
)

router = APIRouter(prefix="/goal", tags=["目标模块"])

@router.post("/",response_model=GoalResponse)
async def create(
    data: GoalCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Main_User = Depends(get_current_user)
):
    return await create_goal_services(db, data, current_user)


@router.get("/{goal_id}", response_model=GoalResponse)
async def get_detail(
    goal_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Main_User = Depends(get_current_user)
):
    return await get_one_goal_svs(db, goal_id, current_user)


@router.get("/", response_model=list[GoalResponse])
async def list_my(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: Main_User = Depends(get_current_user)
):
    return await get_all_goal_svs(db, current_user, skip=skip, limit=limit)


@router.put("/{goal_id}", response_model=GoalResponse)
async def update(
    goal_id: int,
    data: GoalUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: Main_User = Depends(get_current_user)
):
    return await update_goal_svs(db, goal_id, data, current_user)


@router.delete("/{goal_id}")
async def delete(
    goal_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Main_User = Depends(get_current_user)
):
    await delete_goal_svs(db, goal_id, current_user)
    return {"msg": "删除成功"}