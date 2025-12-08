from pydantic_settings import BaseSettings
from typing import List
import secrets
import logging

logger = logging.getLogger("schedule_planning.config")


class Settings(BaseSettings):
    PROJECT_NAME: str = "Sistema Asignación Aulas UNSA"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # Database - provide a local sqlite default for development/testing
    DATABASE_URL: str = "postgresql+psycopg2://postgres:123456@localhost:5432/postgres"

    # Security - if not set in environment, a runtime secret will be generated
    SECRET_KEY: str = ""
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000"]

    # Redis (optional for caching)
    REDIS_URL: str = "redis://localhost:6379"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

# If SECRET_KEY was not provided via env/.env, generate a temporary one and warn.
if not settings.SECRET_KEY:
    generated = secrets.token_urlsafe(32)
    settings.SECRET_KEY = generated
    logger.warning("No SECRET_KEY was set; generated a temporary key for this process. Set SECRET_KEY in env for production.")
