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

    # Database (Cloudflare D1 — required)
    CF_ACCOUNT_ID: Optional[str] = None
    D1_DATABASE_ID: Optional[str] = None
    D1_API_TOKEN: Optional[str] = None

    # Authentication credentials
    API_USERNAME: str = "admin"
    API_TOKEN: Optional[str] = "token"
    SECRET_KEY: Optional[str] = "secret"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Admin token installed on boot when provided (deployment secret)
    BOOT_TOKEN: Optional[str] = None

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

    @property
    def d1_enabled(self) -> bool:
        return bool(self.CF_ACCOUNT_ID and self.D1_DATABASE_ID and self.D1_API_TOKEN)


settings = Settings()
