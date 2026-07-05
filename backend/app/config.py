"""
Project Atlas Configuration

Centralized application configuration using Pydantic Settings.

This module provides a single source of truth for all runtime
configuration. Every component in Atlas should import the shared
`settings` instance instead of reading environment variables directly.
"""

from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Strongly typed application settings.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    project_name: str = "Project Atlas"
    app_version: str = "0.1.0-alpha"

    environment: Literal[
        "development",
        "staging",
        "production",
    ] = "development"

    debug: bool = False

    log_level: Literal[
        "DEBUG",
        "INFO",
        "WARNING",
        "ERROR",
        "CRITICAL",
    ] = "INFO"

    database_url: str = (
        "postgresql+asyncpg://postgres:postgres@postgres:5432/atlas"
    )

    redis_url: str = "redis://redis:6379/0"

    cors_origins: list[str] = [
        "http://localhost:3000",
    ]


#: Global application settings instance.
settings = Settings()