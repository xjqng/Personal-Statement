"""
日记接口，全部需要登录鉴权
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from db.session import get_db
from api.deps import get_current_user
from models.models import Main_User
from schemas.diaries import DiaryCreate, DiaryUpdate, DiaryResponse
from services.diaries import (
    create_diary_service,
    get_diary_detail_service,
    list_my_diaries_service,
    update_diary_service,
    delete_diary_service
)

router = APIRouter(prefix="/diary", tags=["日记"])


@router.post("/", response_model=DiaryResponse)
async def create(
    data: DiaryCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Main_User = Depends(get_current_user)
):
    return await create_diary_service(db, data, current_user)


@router.get("/{diary_id}", response_model=DiaryResponse)
async def get_detail(
    diary_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Main_User = Depends(get_current_user)
):
    return await get_diary_detail_service(db, diary_id, current_user)


@router.get("/", response_model=list[DiaryResponse])
async def list_my(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: Main_User = Depends(get_current_user)
):
    return await list_my_diaries_service(db, current_user, skip=skip, limit=limit)


@router.put("/{diary_id}", response_model=DiaryResponse)
async def update(
    diary_id: int,
    data: DiaryUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: Main_User = Depends(get_current_user)
):
    return await update_diary_service(db, diary_id, data, current_user)


@router.delete("/{diary_id}")
async def delete(
    diary_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Main_User = Depends(get_current_user)
):
    await delete_diary_service(db, diary_id, current_user)
    return {"msg": "删除成功"}
