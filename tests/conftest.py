"""
pytest 公共夹具：测试数据库 + httpx 异步客户端 + 认证头
"""
import os
import sys
from pathlib import Path

# ===== 必须在所有项目导入之前设置环境变量 =====
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["DEBUG"] = "False"

# 将 src 目录加入 sys.path
project_root = Path(__file__).resolve().parent.parent
src_dir = project_root / "src"
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(src_dir))

import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import StaticPool

from main import app
from db.session import Base, get_db
import models.models  # noqa: F401 确保模型被注册

# ===== 测试专用引擎（内存SQLite + StaticPool） =====
test_engine = create_async_engine(
    "sqlite+aiosqlite:///:memory:",
    poolclass=StaticPool,
    connect_args={"check_same_thread": False},
)
TestSessionLocal = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)


async def override_get_db():
    """测试用数据库会话，替代生产 get_db"""
    async with TestSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


app.dependency_overrides[get_db] = override_get_db


@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    """每个测试前后自动建表/清表"""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def client():
    """httpx 异步测试客户端，直连 ASGI app"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
async def auth_headers(client):
    """注册并登录测试用户，返回认证请求头"""
    await client.post("/auth/register", json={
        "username": "testuser",
        "email": "test@test.com",
        "password": "test12345"
    })
    resp = await client.post("/auth/login", data={
        "username": "testuser",
        "password": "test12345"
    })
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
