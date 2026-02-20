from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
import os
from typing import Literal, Optional

ROOT_DIR = Path.cwd()


class Settings(BaseSettings):
    # Application configuration
    SERVICE: str = "slaterunner_api"
    DESC: str = "RESTful FastAPI for fixing it in post."
    VERSION: str = "0.0.1"
    API_VERSION: str = "v1"
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL", "RESET"] = "INFO"

    # Deployment environment
    ENVIRONMENT: Literal["development", "staging", "production"] = "development"
    DEBUG: bool = False

    # Database connection parameters
    DB_HOST: str | None = None
    DB_PORT: int = 6543
    DB_NAME: str | None = None
    DB_USER: str | None = None
    DB_PASSWORD: str | None = None
    DB_SSLMODE: str = "disable"
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10

    # Authentication credentials
    API_USERNAME: str = "admin"
    API_TOKEN: Optional[str] = "token"
    SECRET_KEY: Optional[str] = "secret"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Cross-origin resource sharing
    CORS_ORIGINS: list[str] = ["*"]

    # Request rate limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60

    model_config = SettingsConfigDict(
        env_file=os.path.join(ROOT_DIR, ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,
    )

    @field_validator("LOG_LEVEL", mode="before")
    def normalize_log_level(cls, v):
        if isinstance(v, str):
            return v.upper()
        return v

    def is_development(self) -> bool:
        return self.ENVIRONMENT == "development"

    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"


settings = Settings()
