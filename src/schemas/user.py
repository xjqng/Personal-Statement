from pydantic import BaseModel

class UserCreate(BaseModel):
    """
    创建用户面板请求
    """

    headshot: str | None = None    
    name: str | None = None
    age: int | None = None

class UserUpdate(BaseModel):
    """
    更新请求
    所有字段均为可选，仅更新用户提交的字段，未提供的字段保持原值不变。
    """
    headshot: str | None = None
    name: str | None = None
    age: int | None = None

class UserResponse(BaseModel):
    """个人资料响应"""
    id: int
    headshot: str | None = None
    name: str | None = None
    age: int | None = None

    model_config = {"from_attributes": True}
