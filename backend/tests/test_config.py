"""
Test configuration loading and validation
"""
import pytest
import os
from app.config import Settings


def test_settings_default_values():
    """Test that default settings are loaded correctly"""
    
    # Invalid URL
    with pytest.raises(ValueError, match="DATABASE_URL must be a PostgreSQL connection string"):
        Settings(DATABASE_URL="mysql://user:pass@localhost:3306/db")


def test_port_validation():
    """Test port number validation"""
    # Valid ports
    valid_ports = [1, 8000, 65535]
    for port in valid_ports:
        settings = Settings(PORT=port)
        assert settings.PORT == port
    
    # Invalid ports
    invalid_ports = [0, -1, 65536, 99999]
    for port in invalid_ports:
        with pytest.raises(ValueError, match="PORT must be between 1 and 65535"):
            Settings(PORT=port)


def test_access_token_expire_validation():
    """Test access token expiration validation"""
    # Valid values
    valid_minutes = [1, 30, 60, 1440]
    for minutes in valid_minutes:
        settings = Settings(ACCESS_TOKEN_EXPIRE_MINUTES=minutes)
        assert settings.ACCESS_TOKEN_EXPIRE_MINUTES == minutes
    
    # Invalid values
    with pytest.raises(ValueError, match="ACCESS_TOKEN_EXPIRE_MINUTES must be positive"):
        Settings(ACCESS_TOKEN_EXPIRE_MINUTES=0)
    
    with pytest.raises(ValueError, match="ACCESS_TOKEN_EXPIRE_MINUTES must be positive"):
        Settings(ACCESS_TOKEN_EXPIRE_MINUTES=-1)
    
    with pytest.raises(ValueError, match="should not exceed 24 hours"):
        Settings(ACCESS_TOKEN_EXPIRE_MINUTES=1441)


def test_refresh_token_expire_validation():
    """Test refresh token expiration validation"""
    # Valid values
    settings = Settings(REFRESH_TOKEN_EXPIRE_MINUTES=10080)  # 7 days
    assert settings.REFRESH_TOKEN_EXPIRE_MINUTES == 10080
    
    # Invalid values
    with pytest.raises(ValueError, match="REFRESH_TOKEN_EXPIRE_MINUTES must be positive"):
        Settings(REFRESH_TOKEN_EXPIRE_MINUTES=0)
    
    with pytest.raises(ValueError, match="REFRESH_TOKEN_EXPIRE_MINUTES must be positive"):
        Settings(REFRESH_TOKEN_EXPIRE_MINUTES=-1)


def test_rate_limit_validation():
    """Test rate limit validation"""
    # Valid values
    valid_limits = [1, 60, 100, 1000]
    for limit in valid_limits:
        settings = Settings(RATE_LIMIT_PER_MINUTE=limit)
        assert settings.RATE_LIMIT_PER_MINUTE == limit
    
    # Invalid values
    with pytest.raises(ValueError, match="RATE_LIMIT_PER_MINUTE must be positive"):
        Settings(RATE_LIMIT_PER_MINUTE=0)
    
    with pytest.raises(ValueError, match="RATE_LIMIT_PER_MINUTE must be positive"):
        Settings(RATE_LIMIT_PER_MINUTE=-1)
    
    with pytest.raises(ValueError, match="seems too high"):
        Settings(RATE_LIMIT_PER_MINUTE=10001)


def test_all_field_types():
    """Test that all fields have correct types"""
    settings = Settings()
    
    # String fields
    assert isinstance(settings.DATABASE_URL, str)
    assert isinstance(settings.API_V1_STR, str)
    assert isinstance(settings.PROJECT_NAME, str)
    assert isinstance(settings.PROJECT_VERSION, str)
    assert isinstance(settings.PROJECT_DESCRIPTION, str)
    assert isinstance(settings.SECRET_KEY, str)
    assert isinstance(settings.ALGORITHM, str)
    assert isinstance(settings.ENVIRONMENT, str)
    assert isinstance(settings.HOST, str)
    
    # Integer fields
    assert isinstance(settings.ACCESS_TOKEN_EXPIRE_MINUTES, int)
    assert isinstance(settings.REFRESH_TOKEN_EXPIRE_MINUTES, int)
    assert isinstance(settings.PORT, int)
    assert isinstance(settings.RATE_LIMIT_PER_MINUTE, int)
    
    # Boolean fields
    assert isinstance(settings.DEBUG, bool)
    
    # List fields
    assert isinstance(settings.BACKEND_CORS_ORIGINS, list)


def test_settings_with_env_file(tmp_path, monkeypatch):
    """Test settings loading from .env file"""
    # Create a temporary .env file
    env_file = tmp_path / ".env"
    env_content = """
DATABASE_URL=postgresql://test:test@localhost:5432/test_db
SECRET_KEY=test_secret_key_that_is_long_enough_32_chars
ACCESS_TOKEN_EXPIRE_MINUTES=60
ENVIRONMENT=development
DEBUG=true
PORT=9000
    """.strip()
    
    env_file.write_text(env_content)
    
    # Change to the temp directory
    monkeypatch.chdir(tmp_path)
    
    # Create settings (should load from .env)
    settings = Settings()
    
    assert settings.DATABASE_URL == "postgresql://test:test@localhost:5432/test_db"
    assert settings.SECRET_KEY == "test_secret_key_that_is_long_enough_32_chars"
    assert settings.ACCESS_TOKEN_EXPIRE_MINUTES == 60
    assert settings.ENVIRONMENT == "development"
    assert settings.DEBUG is True
    assert settings.PORT == 9000
