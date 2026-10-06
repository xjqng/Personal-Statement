# core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # 基础调试
    DEBUG: bool = False
    # 数据库
    DATABASE_URL: str
    # JWT鉴权
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # AI 对话（OpenAI 兼容接口，支持 DeepSeek / Qwen / OpenAI 等）
    AI_API_KEY: str = ""
    AI_BASE_URL: str = "https://api.deepseek.com/v1"
    AI_MODEL: str = "deepseek-chat"
    AI_TIMEOUT: int = 30

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        # 重要：生产环境docker部署时，优先读取系统环境变量，覆盖.env
        extra="ignore"
    )


settings = Settings()