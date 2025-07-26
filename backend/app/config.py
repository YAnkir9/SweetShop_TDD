from pydantic import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    """Application settings"""
    
    # Database settings
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:allthebest@localhost:5432/sweet_shop")
    
    # API settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "SweetShop API"
    
    # Security settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "JPJW1IszbG_0L3-VCNL3SfcIpALsQY9sQeiuhFXI2_A")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))  # 30 min for production, override in .env for local
    
    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "production")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Create settings instance
settings = Settings()
