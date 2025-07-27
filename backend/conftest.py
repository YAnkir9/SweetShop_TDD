"""
Test configuration and fixtures for the Sweet Shop application
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    """Provide test client for API testing"""
    with TestClient(app) as test_client:
        yield test_client
