"""Configuration tests."""

import pytest

from dataminer.core.config import Settings


def test_default_settings() -> None:
    """Test default settings values."""
    settings = Settings()
    assert settings.app_name == "dataminer"
    assert settings.app_version == "0.1.0"
    assert settings.api_port == 8000


def test_settings_with_env_override(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test settings can be overridden by environment variables."""
    monkeypatch.setenv("APP_NAME", "test-app")
    monkeypatch.setenv("API_PORT", "9000")
    monkeypatch.setenv("DEBUG", "true")

    settings = Settings()
    assert settings.app_name == "test-app"
    assert settings.api_port == 9000
    assert settings.debug is True


def test_settings_cors_origins_parsing() -> None:
    """Test CORS origins can be parsed from string."""
    settings = Settings(allowed_origins="http://localhost:3000,http://localhost:8000")
    assert len(settings.allowed_origins) == 2
    assert "http://localhost:3000" in settings.allowed_origins


def test_settings_properties() -> None:
    """Test settings computed properties."""
    dev_settings = Settings(environment="development")
    assert dev_settings.is_development is True
    assert dev_settings.is_production is False

    prod_settings = Settings(environment="production")
    assert prod_settings.is_production is True
    assert prod_settings.is_development is False
