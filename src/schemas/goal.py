from datetime import datetime
from pydantic import BaseModel
from models.models import GoalStatus

class GoalCreate(BaseModel):
    """创建目标"""
    title: str
    description: str
    status: GoalStatus
    start_date: datetime
    end_date: datetime


class GoalUpdate(BaseModel):
    """更新目标，局部更新"""
    title: str | None = None
    description: str | None = None
    status: GoalStatus | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None


class GoalResponse(BaseModel):
    """返回目标给前端"""
    id: int
    title: str
    description: str
    status: GoalStatus
    start_date: datetime
    end_date: datetime
    created_at: datetime

    model_config = {"from_attributes": True}
