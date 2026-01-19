"""Application configuration using pydantic-settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Database
    database_url: str

    # Authentication
    better_auth_secret: str
    better_auth_url: str = "http://localhost:3000"

    # Environment
    environment: str = "development"

    # JWT settings
    jwt_algorithm: str = "HS256"
    jwt_expiration_days: int = 7


settings = Settings()
