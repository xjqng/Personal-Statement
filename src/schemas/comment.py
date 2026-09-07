from datetime import datetime
from pydantic import BaseModel

class CommentCreate(BaseModel):
    """创建评论"""
    target_type: str
    target_id: int
    content: str

# 业务不需要编辑评论可以直接删掉CommentUpdate
# class CommentUpdate(BaseModel):
#     content: str | None = None


class CommentResponse(BaseModel):
    """返回评论给前端"""
    id: int
    target_type: str
    target_id: int
    content: str
    user_id:int
    created_at: datetime

    model_config = {"from_attributes": True}
