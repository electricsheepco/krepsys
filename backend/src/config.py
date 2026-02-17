"""Configuration management using Pydantic Settings.

Follows 12-factor app principles:
- Configuration stored in environment variables
- Sensible defaults for development
- Type validation via Pydantic
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )
    
    database_url: str = "sqlite:///./data/krepsys.db"
    port: int = 8080
    allowed_origins: str = "http://localhost:3000,http://krepsys.local"
    fetch_interval: int = 900  # seconds (15 minutes)
    log_level: str = "INFO"
