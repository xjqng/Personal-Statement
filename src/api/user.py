"""
用户个人资料接口
全部需要登录鉴权 Depends(get_current_user)
"""
from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from db.session import get_db
from api.deps import get_current_user
from models.models import Main_User
from schemas.user import UserCreate, UserUpdate, UserResponse
from services.user import get_my_profile_service, create_my_profile_service, update_my_profile_service
from core.upload import save_avatar

router = APIRouter(prefix="/profile", tags=["个人资料"])


@router.get("/", response_model=UserResponse)
async def get_my_profile(
    db: AsyncSession = Depends(get_db),
    current_user: Main_User = Depends(get_current_user)
):
    return await get_my_profile_service(db, current_user)


@router.post("/", response_model=UserResponse)
async def create_my_profile(
    data: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Main_User = Depends(get_current_user)
):
    return await create_my_profile_service(db, data, current_user)


@router.put("/", response_model=UserResponse)
async def update_my_profile(
    data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: Main_User = Depends(get_current_user)
):
    return await update_my_profile_service(db, data, current_user)


@router.post("/avatar", response_model=UserResponse)
async def upload_avatar(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: Main_User = Depends(get_current_user)
):
    """上传头像图片，自动保存并更新资料"""
    avatar_url = await save_avatar(file)
    data = UserUpdate(headshot=avatar_url)
    return await update_my_profile_service(db, data, current_user)
