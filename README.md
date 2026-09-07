# 自白书 · Personal Statement

基于 FastAPI 的个人成长记录系统，支持用户认证、日记、目标、评论等功能。

## 技术栈

- **Web 框架**：FastAPI + Uvicorn（全异步）
- **ORM**：SQLAlchemy 2.0（AsyncSession）
- **数据库**：SQLite（开发）/ MySQL（生产，依赖 `asyncmy`）
- **数据校验**：Pydantic v2 + pydantic-settings
- **认证**：JWT（access + refresh 双 token）+ bcrypt 密码哈希
- **安全**：bleach 防 XSS（富文本白名单 + 纯文本转义）
- **日志**：loguru（按 50MB 切割、保留 7 天、异步 enqueue）
- **包管理**：uv

## 项目结构

```
Personal Statement/
├── main.py                 # 应用入口（注册路由、中间件、生命周期）
├── pyproject.toml          # 依赖与项目配置
├── .env                    # 环境变量（不入库）
└── src/
    ├── api/                # 路由层（接收请求、依赖注入）
    ├── services/           # 业务层（业务校验、调用 CRUD）
    ├── crud/               # 数据访问层（仅数据库操作）
    ├── schemas/            # Pydantic 模型（请求/响应）
    ├── models/             # SQLAlchemy ORM 模型
    ├── core/               # 通用模块（config/security/logger/xss/upload）
    └── db/                 # 引擎与 session 工厂
```

## 快速开始

### 1. 安装依赖

```bash
uv sync
```

### 2. 配置环境变量

在项目根目录创建 `.env`：

```env
DEBUG=True
DATABASE_URL=sqlite+aiosqlite:///./personal_statement.db
SECRET_KEY=your-secret-key-change-me
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7
```

### 3. 启动服务

```bash
uv run python main.py
# 或
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

启动后访问：

- 接口文档（Swagger）：http://127.0.0.1:8000/docs
- ReDoc：http://127.0.0.1:8000/redoc

数据库表会在应用启动时自动创建（开发环境）。

## 接口概览

| 模块 | 前缀 | 说明 | 鉴权 |
| --- | --- | --- | --- |
| 认证 | `/auth` | 注册、登录（OAuth2 表单）、刷新 token | 否 |
| 个人资料 | `/profile` | 查看 / 创建 / 更新当前用户资料 | 是 |
| 日记 | `/diary` | 日记 CRUD，含富文本 XSS 清洗 | 是 |
| 目标 | `/goal` | 目标 CRUD，含状态枚举（未开始/进行中/已完成/已取消） | 是 |
| 评论 | `/comment` | 通用评论（可挂在日记或目标上） | 部分 |

### 认证流程

1. `POST /auth/register` 注册 → 返回 access/refresh token
2. `POST /auth/login`（OAuth2PasswordRequestForm）登录 → 返回 access/refresh token
3. access token 过期后，`POST /auth/refresh` 用 refresh token 换新的 access token
4. 后续受保护接口请求头携带：`Authorization: Bearer <access_token>`

## 安全特性

- **密码**：bcrypt 加盐哈希
- **JWT**：access / refresh 双 token
- **归属校验**：日记 / 目标的查询、修改、删除均校验 `user_id` 归属
- **XSS 防护**：
  - 纯文本字段 → `bleach.clean(strip=False)` 全转义
  - 富文本字段 → 白名单标签（`p / b / a / ul ...`），过滤 `javascript:` 伪协议
  - **入库前清洗**，存储型 XSS 在落库时即被拦截
- **文件上传**：类型与大小校验 + UUID 重命名，防路径遍历

## 开发约定

- `api` 层只做参数接收与依赖注入
- `services` 层负责业务校验、权限检查、调用 CRUD，不写 SQL
- `crud` 层只做数据库操作，不做业务判断
- 所有受保护接口通过 `Depends(get_current_user)` 获取当前用户

## License

MIT
