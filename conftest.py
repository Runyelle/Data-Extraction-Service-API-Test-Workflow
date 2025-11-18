"""
Pytest configuration and fixtures for API tests.
"""
import pytest
import logging
from typing import Generator

from utils.api_client import APIClient
from utils.database_seeder import DatabaseSeeder
from config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@pytest.fixture(scope="session")
def api_client() -> APIClient:
    """Create an API client instance for the test session."""
    return APIClient()


@pytest.fixture(scope="session")
def db_seeder() -> Generator[DatabaseSeeder, None, None]:
    """Create a database seeder instance for the test session."""
    seeder = DatabaseSeeder()
    yield seeder
    seeder.close()


@pytest.fixture(autouse=True)
def setup_test_environment():
    """Setup and teardown for each test."""
    # Setup
    logger.info("Setting up test environment")
    yield
    # Teardown
    logger.info("Tearing down test environment")


@pytest.fixture
def service_provided_token() -> str:
    """Get the service provided API token from settings."""
    token = settings.service_provided_api_token
    if not token:
        pytest.skip("SERVICE_PROVIDED_API_TOKEN not configured")
    return token

