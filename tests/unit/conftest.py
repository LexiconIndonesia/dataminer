"""Unit test configuration - no external dependencies."""

import pytest

from dataminer.core.config import Settings


@pytest.fixture
def test_settings() -> Settings:
    """Create test settings for unit tests."""
    return Settings(
        environment="development",
        debug=True,
        log_level="DEBUG",
        database_url="postgresql://dataminer:password@localhost:5432/dataminer_test",
        redis_url="redis://localhost:6379/1",
    )
