"""Tests for configuration management."""
import os
import pytest
from src.config import Settings


def test_settings_loads_from_environment():
    """Test that Settings correctly loads values from environment variables."""
    # Set environment variables
    os.environ["DATABASE_URL"] = "postgresql://test:test@localhost/testdb"
    os.environ["PORT"] = "9000"
    os.environ["ALLOWED_ORIGINS"] = "http://test1.com,http://test2.com"
    os.environ["FETCH_INTERVAL"] = "600"
    os.environ["LOG_LEVEL"] = "DEBUG"
    
    # Create settings instance
    settings = Settings()
    
    # Verify values are loaded from environment
    assert settings.database_url == "postgresql://test:test@localhost/testdb"
    assert settings.port == 9000
    assert settings.allowed_origins == "http://test1.com,http://test2.com"
    assert settings.fetch_interval == 600
    assert settings.log_level == "DEBUG"
    
    # Cleanup
    del os.environ["DATABASE_URL"]
    del os.environ["PORT"]
    del os.environ["ALLOWED_ORIGINS"]
    del os.environ["FETCH_INTERVAL"]
    del os.environ["LOG_LEVEL"]


def test_settings_has_sensible_defaults():
    """Test that Settings has sensible default values when no env vars are set."""
    # Ensure no relevant env vars are set
    env_vars = ["DATABASE_URL", "PORT", "ALLOWED_ORIGINS", "FETCH_INTERVAL", "LOG_LEVEL"]
    original_values = {}
    for var in env_vars:
        if var in os.environ:
            original_values[var] = os.environ[var]
            del os.environ[var]
    
    # Create settings instance
    settings = Settings()
    
    # Verify default values
    assert settings.database_url == "sqlite:///./data/krepsys.db"
    assert settings.port == 8080
    assert settings.allowed_origins == "http://localhost:3000,http://krepsys.local"
    assert settings.fetch_interval == 900
    assert settings.log_level == "INFO"
    
    # Restore original environment
    for var, value in original_values.items():
        os.environ[var] = value
