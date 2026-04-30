"""
Application Configuration Module
Handles all environment variables and application settings
"""

from pydantic_settings import BaseSettings
from typing import Optional
from functools import lru_cache


class Settings(BaseSettings):
    """Main application settings"""

    # Telegram Configuration
    telegram_bot_token: str
    telegram_admin_id: int

    # Database Configuration
    database_url: str
    database_echo: bool = False

    # FastAPI Configuration
    fastapi_host: str = "0.0.0.0"
    fastapi_port: int = 8000
    fastapi_reload: bool = True

    # AI/LLM Configuration
    openrouter_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    ai_model: str = "gpt-3.5-turbo"

    # Redis Configuration
    redis_url: str = "redis://localhost:6379/0"

    # JWT Configuration
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Application Settings
    debug: bool = True
    log_level: str = "INFO"
    max_file_size: int = 52428800  # 50MB
    allowed_file_types: str = "pdf,epub,txt"

    # Email Configuration
    smtp_server: Optional[str] = None
    smtp_port: Optional[int] = None
    smtp_user: Optional[str] = None
    smtp_password: Optional[str] = None

    # S3 Configuration
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    aws_bucket_name: Optional[str] = None

    # Backup Configuration
    backup_schedule: str = "0 2 * * *"
    backup_retention_days: int = 30

    class Config:
        env_file = ".env"
        case_sensitive = False

    @property
    def allowed_extensions(self) -> list:
        """Get list of allowed file extensions"""
        return self.allowed_file_types.split(",")

    @property
    def database_settings(self) -> dict:
        """Get database connection settings"""
        return {
            "url": self.database_url,
            "echo": self.database_echo,
            "pool_pre_ping": True,
            "pool_size": 20,
            "max_overflow": 10,
        }


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Export settings instance
settings = get_settings()
