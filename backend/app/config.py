from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
import os

class Settings(BaseSettings):
    DATABASE_URL: str = Field(default="postgresql://postgres:allthebest@localhost:5432/sweet_shop")
    API_V1_STR: str = Field(default="/api/v1")
    PROJECT_NAME: str = Field(default="SweetShop API")
    PROJECT_VERSION: str = Field(default="1.0.0")
    PROJECT_DESCRIPTION: str = Field(default="A TDD-developed sweet shop management system")
    SECRET_KEY: str = Field(default="JPJW1IszbG_0L3-VCNL3SfcIpALsQY9sQeiuhFXI2_A")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30)
    REFRESH_TOKEN_EXPIRE_MINUTES: int = Field(default=60 * 24 * 7)
    ALGORITHM: str = Field(default="HS256")
    ENVIRONMENT: str = Field(default="production")
    DEBUG: bool = Field(default=False)
    BACKEND_CORS_ORIGINS: List[str] = Field(default=["http://localhost:3000", "http://localhost:5173", "http://localhost:8080"])
    HOST: str = Field(default="0.0.0.0")
    PORT: int = Field(default=8000)
    RATE_LIMIT_PER_MINUTE: int = Field(default=60)

    @field_validator("DATABASE_URL")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        """Validate database URL format"""
        if not v.startswith(("postgresql://", "postgres://")):
            raise ValueError("DATABASE_URL must be a PostgreSQL connection string")
        return v
    
    @field_validator("PORT")
    @classmethod
    def validate_port(cls, v: int) -> int:
        """Validate port number range"""
        if not (1 <= v <= 65535):
            raise ValueError("PORT must be between 1 and 65535")
        return v
    
    @field_validator("ACCESS_TOKEN_EXPIRE_MINUTES")
    @classmethod
    def validate_access_token_expire(cls, v: int) -> int:
        """Validate access token expiration"""
        if v <= 0:
            raise ValueError("ACCESS_TOKEN_EXPIRE_MINUTES must be positive")
        if v > 1440:
            raise ValueError("ACCESS_TOKEN_EXPIRE_MINUTES should not exceed 24 hours (1440 minutes)")
        return v
    
    @field_validator("REFRESH_TOKEN_EXPIRE_MINUTES")
    @classmethod
    def validate_refresh_token_expire(cls, v: int) -> int:
        """Validate refresh token expiration"""
        if v <= 0:
            raise ValueError("REFRESH_TOKEN_EXPIRE_MINUTES must be positive")
        return v
    
    @field_validator("RATE_LIMIT_PER_MINUTE")
    @classmethod
    def validate_rate_limit(cls, v: int) -> int:
        """Validate rate limit value"""
        if v <= 0:
            raise ValueError("RATE_LIMIT_PER_MINUTE must be positive")
        if v > 10000:
            raise ValueError("RATE_LIMIT_PER_MINUTE seems too high, maximum 10000")
        return v
    
    @field_validator("ENVIRONMENT")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """Validate environment values"""
        allowed_envs = ["development", "staging", "production"]  
        if v not in allowed_envs:
            raise ValueError(f"Environment must be one of {allowed_envs}")
        return v
    
    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        """Validate secret key length"""
        if len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long")
        return v
    
    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v):
        """Parse CORS origins from string or list"""
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError("BACKEND_CORS_ORIGINS must be a list or comma-separated string")
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

settings = Settings()
