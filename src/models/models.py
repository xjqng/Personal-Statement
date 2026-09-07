from __future__ import annotations
from datetime import datetime, date
from sqlalchemy.orm import Mapped, mapped_column
from db.session import Base
from sqlalchemy import (
    Integer, Enum as SQLEnum, ForeignKey, String, Text, Boolean, DateTime
)
import enum


class Main_User(Base):
    __tablename__ = "main_user"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, comment="用户主键ID")
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, comment="用户名（唯一）")
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True, comment="邮箱（唯一）")
    hashed_password: Mapped[str] = mapped_column(String(255), comment="加密后的密码")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, comment="账号是否激活")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, comment="创建时间")
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")


class User(Base):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, comment="用户资料主键ID")
    headshot: Mapped[str | None] = mapped_column(String(500), default=None, comment="头像URL")
    name: Mapped[str | None] = mapped_column(String(50), default=None, comment="名称")
    age: Mapped[int | None] = mapped_column(Integer, default=None, comment="年龄")
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("main_user.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        comment="关联登录账号ID"
    )


class Diary(Base):
    __tablename__ = "diaries"
    id: Mapped[int] = mapped_column(primary_key=True, index=True, comment="日记主键ID")
    title: Mapped[str] = mapped_column(String(200), nullable=False, comment="日记标题")
    content: Mapped[str] = mapped_column(Text, nullable=False, comment="日记内容")
    created_at: Mapped[datetime] = mapped_column(default=datetime.now, comment="创建时间")
    updated_at: Mapped[datetime] = mapped_column(default=datetime.now, onupdate=datetime.now, comment="更新时间")
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("main_user.id", ondelete="CASCADE"),
        nullable=False,
        comment="所属用户ID"
    )


class GoalStatus(str, enum.Enum):
    NOT_STARTED = "未开始"
    IN_PROGRESS = "进行中"
    COMPLETED = "已完成"
    CANCELLED = "已取消"


class Goal(Base):
    __tablename__ = "goal"
    id: Mapped[int] = mapped_column(primary_key=True, index=True, comment="目标ID")
    title: Mapped[str] = mapped_column(String(200), nullable=False, comment="目标标题")
    description: Mapped[str | None] = mapped_column(Text, default=None, comment="目标描述")
    status: Mapped[GoalStatus] = mapped_column(SQLEnum(GoalStatus), default=GoalStatus.NOT_STARTED, comment="目标状态")
    start_date: Mapped[date | None] = mapped_column(default=None, comment="开始日期")
    end_date: Mapped[date | None] = mapped_column(default=None, comment="结束日期")
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("main_user.id", ondelete="CASCADE"),
        nullable=False,
        comment="所属用户"
    )


class Comment(Base):
    __tablename__ = "comments"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    target_type: Mapped[str] = mapped_column(String(50), nullable=False, comment="目标类型: diary, goal")
    target_id: Mapped[int] = mapped_column(nullable=False, index=True, comment="目标ID")
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("main_user.id", ondelete="CASCADE"),
        nullable=False,
        comment="评论人ID"
    )