from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from db.session import get_db
from api.deps import get_current_user
from models.models import Main_User
from schemas.comment import CommentCreate, CommentResponse
from services.comment import (
    create_comment_service,
    get_comment_detail_service,
    list_target_comment_service,
    delete_comment_service
)

router = APIRouter(prefix="/comment", tags=["通用评论模块"])


@router.post("/", response_model=CommentResponse)
async def create(
    data: CommentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Main_User = Depends(get_current_user)
):
    return await create_comment_service(db, data, current_user)


# 查询某目标下评论，target_type传diary或goal
# 注意：这条路由必须放在 /{comment_id} 前面，否则 /list 会被 /{comment_id} 抢匹配
@router.get("/list", response_model=list[CommentResponse])
async def list_target_comment(
    target_type: str,
    target_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    db: AsyncSession = Depends(get_db)
):
    return await list_target_comment_service(db, target_type, target_id, skip, limit)


@router.get("/{comment_id}", response_model=CommentResponse)
async def get_detail(
    comment_id: int,
    db: AsyncSession = Depends(get_db)
):
    return await get_comment_detail_service(db, comment_id)


@router.delete("/{comment_id}")
async def delete(
    comment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Main_User = Depends(get_current_user)
):
    await delete_comment_service(db, comment_id, current_user)
    return {"msg": "删除评论成功"}
