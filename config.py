# config.py
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # 服务配置
    APP_NAME: str = "Festival Query API"
    APP_VERSION: str = "1.0.0"
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # API配置
    TIMOR_API_BASE: str = "https://timor.tech/api/holiday"
    REQUEST_TIMEOUT: int = 5

    # 缓存配置（秒）
    CACHE_TTL: int = 3600  # 1小时

    # CORS允许的来源
    ALLOW_ORIGINS: list = ["*"]

    class Config:
        env_file = ".env"


settings = Settings()