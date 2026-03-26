"""Application configuration management via environment variables.

This module loads sensitive configuration values from .env files
using Pydantic Settings for validation and type safety.
"""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


# Locate .env.bot.secret file in project hierarchy
BASE_DIR = Path(__file__).resolve().parent
ENV_FILE = BASE_DIR / ".env.bot.secret"
if not ENV_FILE.exists():
    ENV_FILE = BASE_DIR.parent / ".env.bot.secret"


class BotConfiguration(BaseSettings):
    """Application settings container with validated environment variables.

    All sensitive configuration values are loaded from .env.bot.secret
    and validated at application startup.
    """

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Telegram Bot API authentication token
    bot_token: str

    # LMS backend API endpoint and authentication
    lms_api_base_url: str
    lms_api_key: str

    # Large Language Model API credentials (used for intent routing)
    llm_api_key: str = ""
    llm_api_base_url: str = ""
    llm_api_model: str = "coder-model"


# Global configuration instance for application-wide access
configuration = BotConfiguration()
