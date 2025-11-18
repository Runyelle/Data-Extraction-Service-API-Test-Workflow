"""
Configuration management for the Data Extraction Service API tests.
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Configuration
    api_base_url: str = Field(default="http://localhost:8000", env="API_BASE_URL")
    api_timeout: int = Field(default=30, env="API_TIMEOUT")
    
    # Database Configuration (for seeded data tests)
    db_host: Optional[str] = Field(default=None, env="DB_HOST")
    db_port: Optional[int] = Field(default=5432, env="DB_PORT")
    db_name: Optional[str] = Field(default=None, env="DB_NAME")
    db_user: Optional[str] = Field(default=None, env="DB_USER")
    db_password: Optional[str] = Field(default=None, env="DB_PASSWORD")
    
    # Service Provided API Token (for real extraction tests)
    service_provided_api_token: Optional[str] = Field(
        default=None, env="SERVICE_PROVIDED_API_TOKEN"
    )
    
    # Test Configuration
    poll_interval_seconds: int = Field(default=5, env="POLL_INTERVAL_SECONDS")
    max_poll_attempts: int = Field(default=120, env="MAX_POLL_ATTEMPTS")
    test_data_cleanup: bool = Field(default=True, env="TEST_DATA_CLEANUP")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()

