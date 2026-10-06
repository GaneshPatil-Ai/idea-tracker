"""Configuration settings for Idea Tracker."""

from enum import Enum
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class AppEnv(str, Enum):
    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"


class LLMProviderType(str, Enum):
    OLLAMA = "ollama"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"


class Settings(BaseSettings):
    """Application settings loaded from environment variables or .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # General
    app_name: str = "Idea Tracker"
    app_env: AppEnv = AppEnv.DEVELOPMENT
    debug: bool = False

    # Database
    database_url: str = "sqlite:///ideas.db"

    # Server
    host: str = "127.0.0.1"
    port: int = 8000

    # Logging
    log_level: str = "INFO"
    log_format: str = "console"  # console or json

    # AI Config
    llm_provider: LLMProviderType = LLMProviderType.OLLAMA
    llm_model: str = "llama3.2"

    # Ollama
    ollama_base_url: str = "http://localhost:11434"

    # OpenAI
    openai_api_key: str | None = None
    openai_base_url: str | None = None

    # Anthropic
    anthropic_api_key: str | None = None

    @property
    def is_testing(self) -> bool:
        return self.app_env == AppEnv.TESTING

    @property
    def db_path(self) -> Path:
        if self.database_url.startswith("sqlite:///"):
            return Path(self.database_url.replace("sqlite:///", ""))
        return Path("ideas.db")


settings = Settings()
