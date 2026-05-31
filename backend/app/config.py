from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional
import secrets


class Settings(BaseSettings):
    DATABASE_URL: str = ""
    OPENAI_API_KEY: str = ""
    JWT_SECRET: str = secrets.token_hex(32)
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 10080  # 7 days
    FRONTEND_URL: str = "http://localhost:3000"
    UPLOAD_DIR: str = "/tmp/uploads"
    MAX_FILE_SIZE_MB: int = 10
    DEBUG: bool = True

    # Optional integrations
    WHATSAPP_API_TOKEN: Optional[str] = None
    WHATSAPP_PHONE_NUMBER_ID: Optional[str] = None

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
