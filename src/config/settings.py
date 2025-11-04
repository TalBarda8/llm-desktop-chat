"""
Application configuration using Pydantic Settings
Reads from environment variables and .env file
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Application configuration settings"""

    # Ollama API settings
    ollama_base_url: str = "http://localhost:11434"
    default_model: str = "llama2"

    # UI settings
    window_title: str = "Local LLM Chat"
    window_width: int = 900
    window_height: int = 700

    # Logging settings
    log_level: str = "INFO"
    log_file: str = "logs/app.log"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )


# Global settings instance
settings = Settings()
