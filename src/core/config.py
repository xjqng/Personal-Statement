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

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        # 重要：生产环境docker部署时，优先读取系统环境变量，覆盖.env
        extra="ignore"
    )


settings = Settings()