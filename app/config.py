from typing import Literal
from functools import lru_cache

from pydantic import AnyHttpUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    environment: Literal[
        "development",
        "test",
        "production",
    ] = "development"

    log_level: Literal[
        "DEBUG",
        "INFO",
        "WARNING",
        "ERROR",
        "CRITICAL",
    ] = "INFO"

    market_service_base_url: AnyHttpUrl = "http://127.0.0.1:8001"

    market_service_timeout_seconds: float = Field(
        default=3.0,
        gt=0,
    )

    service_name: str = "product-validation-api"

    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "gemma3"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="APP_",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
