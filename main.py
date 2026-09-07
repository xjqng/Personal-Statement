"""
应用入口：将 src 目录加入 sys.path，注册路由、中间件、生命周期事件
"""
import sys
from pathlib import Path
from contextlib import asynccontextmanager

# main.py 所在目录
project_root = Path(__file__).resolve().parent
# 真正的代码包在 src 子目录下
src_dir = project_root / "src"
sys.path.insert(0, str(src_dir))

# 业务导入
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder
from core.logger import logger

from api.auth import router as auth_router
from api.user import router as user_router
from api.diaries import router as diaries_router
from api.goal import router as goal_router
from api.comment import router as comment_router
from db.session import engine, Base
import models.models  # noqa: F401  确保所有模型被导入注册


# ===== 启动时自动建表（开发环境） =====
@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期：启动时自动创建数据库表"""
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("数据库表初始化完成")
    except Exception as e:
        print("建表发生异常：", e)
    yield
    # 服务关闭时可在此释放资源


app = FastAPI(
    title="自白书",
    version="1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    # 本地开发常用端口：5500 (Live Server) / 5173 (Vite) / 8000 (同源)
    allow_origins=[
        "http://127.0.0.1:5500", "http://localhost:5500",
        "http://127.0.0.1:5173", "http://localhost:5173",
        "http://127.0.0.1:8000", "http://localhost:8000",
    ],
    allow_credentials=True,  # 允许携带 cookie/凭证
    allow_methods=["*"],     # 允许所有请求方式（GET/POST/PUT/DELETE）
    allow_headers=["*"],     # 允许所有请求头
)


# ========== 中间件：请求日志 ==========
@app.middleware("http")
async def request_log_middleware(request: Request, call_next):
    response = await call_next(request)
    logger.info(f"{request.method} {request.url.path} -> {response.status_code}")
    return response


# ========== 统一异常处理 ==========
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.warning(f"HTTP异常: {request.method} {request.url.path} -> {exc.status_code} {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"code": exc.status_code, "message": exc.detail}
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning(f"参数校验失败: {request.method} {request.url.path}")
    return JSONResponse(
        status_code=422,
        content={"code": 422, "message": "参数校验失败", "errors": jsonable_encoder(exc.errors())}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"未处理异常: {request.method} {request.url.path} -> {exc}")
    return JSONResponse(
        status_code=500,
        content={"code": 500, "message": "服务器内部错误"}
    )


app.include_router(auth_router)
app.include_router(user_router)
app.include_router(diaries_router)
app.include_router(goal_router)
app.include_router(comment_router)

# 静态文件服务：头像上传目录
static_dir = project_root / "static"
static_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
