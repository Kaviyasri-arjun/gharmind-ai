"""
GHARMIND AI — Application Configuration
All settings loaded from environment variables with sensible defaults.
"""
from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Application ────────────────────────────────────────────────
    APP_NAME: str = "GHARMIND AI"
    APP_VERSION: str = "1.0.0"
    APP_ENV: Literal["development", "staging", "production"] = "development"
    DEBUG: bool = True
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:3001"]
    SECRET_KEY: str = "dev-secret-key-change-in-production-minimum-32-chars!!"

    # ── Database ───────────────────────────────────────────────────
    DATABASE_URL: str = "postgresql+asyncpg://gharmind:devpassword@localhost:5432/gharmind"
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20
    DATABASE_POOL_TIMEOUT: int = 30

    # ── Redis ──────────────────────────────────────────────────────
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_CACHE_TTL_SECONDS: int = 300  # 5 minutes

    # ── AWS ────────────────────────────────────────────────────────
    AWS_REGION: str = "ap-south-1"
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""

    # ── AWS Bedrock ────────────────────────────────────────────────
    BEDROCK_REGION: str = "ap-south-1"
    BEDROCK_CLAUDE_MODEL_ID: str = "anthropic.claude-3-sonnet-20240229-v1:0"
    BEDROCK_CLAUDE_HAIKU_MODEL_ID: str = "anthropic.claude-3-haiku-20240307-v1:0"
    BEDROCK_TITAN_EMBED_MODEL_ID: str = "amazon.titan-embed-text-v1"
    BEDROCK_MAX_RETRIES: int = 3
    BEDROCK_TIMEOUT_SECONDS: int = 30
    BEDROCK_MOCK_RESPONSES: bool = False  # Set True for local dev without AWS

    # ── AWS Cognito ────────────────────────────────────────────────
    COGNITO_USER_POOL_ID: str = ""
    COGNITO_APP_CLIENT_ID: str = ""
    COGNITO_REGION: str = "ap-south-1"
    SKIP_AUTH: bool = True  # Set False in production

    # ── Twin Engine ────────────────────────────────────────────────
    TWIN_TICK_INTERVAL_SECONDS: int = 60
    PREDICTION_INTERVAL_SECONDS: int = 300  # 5 minutes
    HISTORICAL_SIM_DAYS: int = 30

    # ── Feature Flags ──────────────────────────────────────────────
    ENABLE_STREAMING_CHAT: bool = True
    ENABLE_WHATIF_SIMULATOR: bool = True
    ENABLE_PATTERN_LEARNING: bool = True

    # ── Indian Context ─────────────────────────────────────────────
    DEFAULT_TIMEZONE: str = "Asia/Kolkata"
    DEFAULT_LANGUAGE: str = "hinglish"

    @field_validator("API_CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors(cls, v: str | list[str]) -> list[str]:
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    @property
    def is_production(self) -> bool:
        return self.APP_ENV == "production"

    @property
    def is_development(self) -> bool:
        return self.APP_ENV == "development"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
