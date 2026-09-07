from datetime import datetime
from pydantic import BaseModel


class DiaryCreate(BaseModel):
    """创建日记"""
    title: str
    content: str


class DiaryUpdate(BaseModel):
    """更新日记，部分更新"""
    title: str | None = None
    content: str | None = None


class DiaryResponse(BaseModel):
    """日记传前端"""
    id: int
    title: str
    content: str
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}
